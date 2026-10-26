"""TerraGuard AI: Evidence reconciliation demo.

Uses simulated observations only.
Not for real emergency decisions.
"""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT_DIR / "sample_flood_evidence.json"
OUTPUT_FILE = ROOT_DIR / "incident_brief.json"

# Fixed reference time for a reproducible simulated demonstration.
AS_OF = datetime.fromisoformat("2026-10-22T08:30:00+05:30")
STALE_AFTER_HOURS = 6
WATER_LEVEL_THRESHOLD_M = 0.2


def parse_timestamp(value):
    """Parse a timestamp and reject missing timezones."""
    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

        if timestamp.tzinfo is None:
            return None

        return timestamp.astimezone(timezone.utc)

    except (ValueError, TypeError, AttributeError):
        return None


def analyze(observations):
    findings = []
    valid = []
    by_location = defaultdict(list)

    reference_time = AS_OF.astimezone(timezone.utc)

    # Validate timestamps and source metadata.
    for item in observations:
        evidence_id = item.get("id", "UNKNOWN-ID")
        source = item.get("source")
        location = item.get("location", "Unknown location")

        by_location[location].append(item)

        if not source:
            findings.append({
                "type": "missing_source",
                "evidence_id": evidence_id,
                "message": "Source name is missing; verify origin."
            })

        timestamp = parse_timestamp(item.get("reported_at"))

        if timestamp is None:
            findings.append({
                "type": "uncertain_timestamp",
                "evidence_id": evidence_id,
                "message": (
                    "Timestamp is missing, invalid, or lacks a timezone."
                )
            })
            continue

        valid.append((item, timestamp))

        age_hours = (
            reference_time - timestamp
        ).total_seconds() / 3600

        if age_hours > STALE_AFTER_HOURS:
            findings.append({
                "type": "stale_evidence",
                "evidence_id": evidence_id,
                "age_hours": round(age_hours, 1),
                "message": (
                    f"Report is {age_hours:.1f} hours old; "
                    "review before relying on it."
                )
            })

        elif age_hours < 0:
            findings.append({
                "type": "future_timestamp",
                "evidence_id": evidence_id,
                "message": (
                    "Timestamp is later than the demo reference time; "
                    "verify it."
                )
            })

    # Detect water-level disagreements within each location.
    for location, items in by_location.items():
        water_items = [
            item for item in items
            if isinstance(item.get("water_level_m"), (int, float))
            and not isinstance(item.get("water_level_m"), bool)
        ]

        if len(water_items) < 2:
            continue

        measurements = [
            item["water_level_m"] for item in water_items
        ]

        if max(measurements) - min(measurements) >= (
            WATER_LEVEL_THRESHOLD_M
        ):
            evidence_ids = [
                item.get("id", "UNKNOWN-ID")
                for item in water_items
            ]

            findings.append({
                "type": "water_level_disagreement",
                "location": location,
                "evidence_ids": evidence_ids,
                "measurements_m": measurements,
                "claims": [
                    {
                        "evidence_id": item.get("id", "UNKNOWN-ID"),
                        "source": item.get("source", "Unknown source"),
                        "reported_at": item.get("reported_at"),
                        "water_level_m": item["water_level_m"]
                    }
                    for item in water_items
                ],
                "message": (
                    "Water-level readings differ by at least 0.2 m. "
                    "Verify sensor timing and calibration."
                )
            })

    locations = sorted({
        item.get("location", "Unknown location")
        for item in observations
    })

    return {
        "title": "TerraGuard AI - Simulated Flood Incident Brief",
        "data_notice": (
            "SIMULATED DEMO DATA ONLY - "
            "not for real emergency decisions."
        ),
        "reference_time": AS_OF.isoformat(),
        "locations": locations,
        "observation_count": len(observations),
        "valid_timestamped_observations": len(valid),
        "findings": findings,
        "assessment": (
            "Human review recommended. "
            "Sample data does not confirm a flood."
        ),
        "recommended_verification": [
            "Check authoritative weather and emergency updates.",
            "Verify conflicting readings with the responsible sensor operator.",
            "Confirm community reports with trained local responders.",
            "Require human review before operational decisions."
        ]
    }


def main():
    if not DATA_FILE.exists():
        raise SystemExit(
            f"Sample file not found: {DATA_FILE}"
        )

    try:
        with DATA_FILE.open("r", encoding="utf-8-sig") as file:
            observations = json.load(file)

    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Invalid JSON in {DATA_FILE}: {exc}"
        )

    if not isinstance(observations, list):
        raise SystemExit(
            "Expected the JSON file to contain a list of observations."
        )

    report = analyze(observations)

    OUTPUT_FILE.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(f"Analyzed {len(observations)} observations.")
    print(f"Found {len(report['findings'])} finding(s).")

    for finding in report["findings"]:
        print(
            f"- [{finding['type']}] {finding['message']}"
        )

    print(f"\nIncident brief saved to: {OUTPUT_FILE}")
    print(report["data_notice"])


if __name__ == "__main__":
    main()