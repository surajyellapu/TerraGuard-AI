"""Load local sample flood evidence.

This is NOT a live Zetaris connection.
It only reads the project's sample_flood_evidence.json file.
"""

import json
from pathlib import Path

# Project root is one folder above this src/ file.
DATA_FILE = Path(__file__).resolve().parent.parent / "sample_flood_evidence.json"

# Clear label so nobody mistakes this for live Zetaris data.
DATA_SOURCE_LABEL = "LOCAL SAMPLE DATA (not live Zetaris)"


def load_sample_flood_evidence():
    """Load sample_flood_evidence.json and check it is a list of records.

    Returns:
        A list of dictionaries from the local sample file.

    Raises:
        FileNotFoundError: if the sample JSON file is missing.
        ValueError: if the JSON is not a list of dictionaries.
    """
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


def main():
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
