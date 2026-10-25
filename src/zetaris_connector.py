
"""Load local sample flood evidence, with an optional Zetaris JDBC client.

The sample JSON loader is NOT a live Zetaris connection.
Live weather rows from NY_TAXI.weather_data are New York taxi-zone weather.
They are not flood evidence and must not be treated as Riverbend Village data.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

# Project root is one folder above this src/ file.
DATA_FILE = Path(__file__).resolve().parent.parent / "sample_flood_evidence.json"

# Clear label so nobody mistakes this for live Zetaris data.
DATA_SOURCE_LABEL = "LOCAL SAMPLE DATA (not live Zetaris)"

DEFAULT_JDBC_URL = "jdbc:zetaris:lightning@localhost:10000"
DEFAULT_JDBC_DRIVER_CLASS = "com.zetaris.lightning.jdbc.LightningDriver"
DEFAULT_JDBC_JAR = (
    r"C:\zetaris-platform\zetaris-platform\jdbc"
    r"\ndp-jdbc-driver-2.4.3.1-7eff043-driver.jar"
)

WEATHER_TABLE = "NY_TAXI.weather_data"
DEFAULT_WEATHER_LIMIT = 5
MAX_WEATHER_LIMIT = 100
WEATHER_SOURCE_NOTE = (
    "New York taxi-zone weather from Zetaris NY_TAXI.weather_data. "
    "Not live flood evidence. Not Riverbend Village data. "
    "Precipitation units and meaning are not verified. "
    "Does not confirm a flood."
)


class ZetarisConfigError(RuntimeError):
    """Raised when JDBC settings or credentials are missing."""


class ZetarisConnectionError(RuntimeError):
    """Raised when the optional live Zetaris connection cannot be used."""


@dataclass(frozen=True)
class ZetarisConfig:
    jdbc_url: str
    driver_class: str
    jar_path: str
    username: str
    password: str


def load_sample_flood_evidence():
    """Load sample_flood_evidence.json and validate its record structure."""
    with DATA_FILE.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Expected a JSON list of records, but got "
            f"{type(data).__name__}."
        )

    for index, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(
                f"Record at index {index} is not a dictionary. "
                f"Got {type(record).__name__}."
            )

    return data


def validate_query_limit(
    limit,
    default=DEFAULT_WEATHER_LIMIT,
    max_limit=MAX_WEATHER_LIMIT,
):
    """Return a safe positive integer limit. Reject arbitrary SQL fragments."""
    if limit is None:
        limit = default

    if isinstance(limit, bool) or not isinstance(limit, int):
        if isinstance(limit, str) and limit.strip().isdigit():
            limit = int(limit.strip())
        else:
            raise ValueError(
                "Query limit must be a positive integer "
                f"between 1 and {max_limit}."
            )

    if limit < 1 or limit > max_limit:
        raise ValueError(
            "Query limit must be a positive integer "
            f"between 1 and {max_limit}."
        )

    return limit


def load_zetaris_config(allow_prompt=False):
    """Load JDBC settings from environment variables."""
    jdbc_url = os.environ.get("ZETARIS_JDBC_URL", DEFAULT_JDBC_URL).strip()
    driver_class = os.environ.get(
        "ZETARIS_JDBC_DRIVER_CLASS",
        DEFAULT_JDBC_DRIVER_CLASS,
    ).strip()
    jar_path = os.environ.get("ZETARIS_JDBC_JAR", DEFAULT_JDBC_JAR).strip()
    username = os.environ.get("ZETARIS_USER", "").strip()
    password = os.environ.get("ZETARIS_PASSWORD")

    if allow_prompt and not username:
        username = input("Zetaris username: ").strip()
    if allow_prompt and not password:
        password = getpass("Zetaris password: ")

    missing = []
    if not username:
        missing.append("ZETARIS_USER")
    if not password:
        missing.append("ZETARIS_PASSWORD")

    if missing:
        raise ZetarisConfigError(
            "Live Zetaris connection is opt-in and is not configured. "
            "Set " + " and ".join(missing) + " in the environment "
            "(or enter them when using the CLI). "
            "The app can continue with local sample flood evidence."
        )

    if not jdbc_url:
        raise ZetarisConfigError("ZETARIS_JDBC_URL is empty.")
    if not driver_class:
        raise ZetarisConfigError("ZETARIS_JDBC_DRIVER_CLASS is empty.")
    if not jar_path:
        raise ZetarisConfigError("ZETARIS_JDBC_JAR is empty.")

    return ZetarisConfig(
        jdbc_url=jdbc_url,
        driver_class=driver_class,
        jar_path=jar_path,
        username=username,
        password=password,
    )


def _to_python_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _close_resources(cursor, connection):
    """Close both resources without masking an active operation error."""
    active_error = sys.exc_info()[1]
    cleanup_error = None

    try:
        if cursor is not None:
            cursor.close()
    except Exception as exc:
        cleanup_error = exc

    try:
        if connection is not None:
            connection.close()
    except Exception as exc:
        if cleanup_error is None:
            cleanup_error = exc

    if cleanup_error is not None:
        if active_error is None:
            raise cleanup_error
        if hasattr(active_error, "add_note"):
            active_error.add_note(
                f"Resource cleanup also failed: {cleanup_error}"
            )


def _fetchall_dicts(cursor):
    description = cursor.description or ()
    column_names = [item[0] for item in description]
    rows = cursor.fetchall() or []
    records = []

    for row in rows:
        record = {}
        for name, value in zip(column_names, row):
            record[name] = _to_python_value(value)
        records.append(record)

    return records


def connect_zetaris(config):
    """Open a JayDeBeApi JDBC connection. Caller must close it."""
    try:
        import jaydebeapi
    except ImportError as exc:
        raise ZetarisConnectionError(
            "JayDeBeApi is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    jar = Path(config.jar_path)
    if not jar.is_file():
        raise ZetarisConnectionError(
            f"JDBC driver JAR was not found at {jar}. "
            "Set ZETARIS_JDBC_JAR to the verified driver path. "
            "The app can continue with local sample flood evidence."
        )

    try:
        return jaydebeapi.connect(
            config.driver_class,
            config.jdbc_url,
            [config.username, config.password],
            str(jar),
        )
    except Exception as exc:
        raise ZetarisConnectionError(
            "Could not connect to Zetaris over JDBC. "
            "Check that Zetaris is running, the driver JAR is correct, "
            "and credentials in the environment are valid. "
            "The app can continue with local sample flood evidence."
        ) from exc


def test_zetaris_connection(config=None, allow_prompt=False):
    """Run SELECT 1. Returns a small result dict. Never prints passwords."""
    config = config or load_zetaris_config(allow_prompt=allow_prompt)
    connection = None
    cursor = None

    try:
        connection = connect_zetaris(config)
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        rows = _fetchall_dicts(cursor)
        return {
            "ok": True,
            "query": "SELECT 1",
            "jdbc_url": config.jdbc_url,
            "rows": rows,
        }
    finally:
        _close_resources(cursor, connection)


def fetch_ny_taxi_weather(
    limit=DEFAULT_WEATHER_LIMIT,
    config=None,
    allow_prompt=False,
):
    """Fetch limited NY_TAXI weather rows, not flood evidence.

    Original column names and values are preserved with source metadata.
    Precipitation units are not verified. Row ordering is unspecified because
    the query has no ORDER BY clause.

    Configuration, connection, and query failures raise exceptions. A
    successful empty result is distinct from a failed fetch.
    """
    safe_limit = validate_query_limit(limit)
    config = config or load_zetaris_config(allow_prompt=allow_prompt)
    connection = None
    cursor = None
    query = f"SELECT * FROM {WEATHER_TABLE} LIMIT {safe_limit}"
    source_rows = None

    try:
        connection = connect_zetaris(config)
        cursor = connection.cursor()
        cursor.execute(query)
        source_rows = _fetchall_dicts(cursor)
    except Exception as exc:
        raise ZetarisConnectionError(
            f"Could not fetch weather preview from {WEATHER_TABLE}."
        ) from exc
    finally:
        _close_resources(cursor, connection)

    records = []
    for row in source_rows:
        record = {
            "_source_system": "zetaris_jdbc",
            "_source_table": WEATHER_TABLE,
            "_source_note": WEATHER_SOURCE_NOTE,
            "_query_limit": safe_limit,
        }
        record.update(row)
        records.append(record)

    return records


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="TerraGuard local sample loader and optional Zetaris JDBC tools."
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Opt-in: run SELECT 1 against Zetaris using env credentials.",
    )
    parser.add_argument(
        "--fetch-weather",
        action="store_true",
        help="Opt-in: fetch NY_TAXI.weather_data rows (not flood evidence).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_WEATHER_LIMIT,
        help=f"Row limit for --fetch-weather (1-{MAX_WEATHER_LIMIT}).",
    )
    args = parser.parse_args(argv)

    if args.test_connection:
        try:
            result = test_zetaris_connection(allow_prompt=True)
        except (ZetarisConfigError, ZetarisConnectionError, ValueError) as exc:
            print(f"Zetaris connection test failed: {exc}")
            return

        print("Zetaris JDBC connection test: OK")
        print(f"JDBC URL: {result['jdbc_url']}")
        print("Query: SELECT 1")
        print(f"Rows: {result['rows']}")
        return

    if args.fetch_weather:
        try:
            records = fetch_ny_taxi_weather(
                limit=args.limit,
                allow_prompt=True,
            )
        except (ZetarisConfigError, ZetarisConnectionError, ValueError) as exc:
            print(f"Zetaris weather preview failed: {exc}")
            return

        print(WEATHER_SOURCE_NOTE)
        print(f"Table: {WEATHER_TABLE}")
        print(f"Record count: {len(records)}")
        print()
        print("First record:")
        print(json.dumps(records[0], indent=2) if records else "No records.")
        return

    records = load_sample_flood_evidence()
    print(DATA_SOURCE_LABEL)
    print(f"File: {DATA_FILE}")
    print(f"Record count: {len(records)}")
    print("Validation: JSON is a list of dictionary records.")
    print()
    print("First record:")
    print(json.dumps(records[0], indent=2) if records else "No records.")


if __name__ == "__main__":
    main()
