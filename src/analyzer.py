
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "sample_flood_evidence.json"


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def analyze(observations):
    findings = []
    valid = []

    for item in observations:
        try:
            timestamp = parse_time(item["reported_at"])
            if timestamp.tzinfo is None:
                raise ValueError("Timezone is missing")
            valid.append((item, timestamp.astimezone(timezone.utc)))
        except (KeyError, TypeError, ValueError):
            findings.append({
                "type": "invalid_observation",
                "evidence_id": item.get("id", "unknown"),
                "message": "Missing or invalid timestamp."
            })

    if not valid:
        return {
            "observation_count": len(observations),
            "findings": findings,
            "assessment": "No valid timestamped observations to assess."
        }

    latest_time = max(timestamp for _, timestamp in valid)

    # Flag reports more than 6 hours older than the newest observation.
    for item, timestamp in valid:
        age_hours = (latest_time - timestamp).total_seconds() / 3600
        if age_hours > 6:
            findings.append({
                "type": "stale_evidence",
                "evidence_id": item.get("id", "unknown"),
                "age_hours": round(age_hours, 1),
                "message": "Older report; review before relying on it."
            })

    # Compare water-level measurements, preserving their source IDs.
    water_levels = [
        (item, item["water_level_m"], timestamp)
        for item, timestamp in valid
        if isinstance(item.get("water_level_m"), (int, float))
    ]

    if len(water_levels) >= 2:
        levels = [entry[1] for entry in water_levels]
        if max(levels) - min(levels) >= 0.2:
            findings.append({
                "type": "water_level_disagreement",
                "evidence_ids": [entry[0].get("id", "unknown")
                                 for entry in water_levels],
                "measurements_m": [entry[1] for entry in water_levels],
                "message": (
                    "Readings differ by at least 0.2 m. "
                    "Verify sensor timing and calibration."
                )
            })

    return {
        "observation_count": len(observations),
        "valid_timestamped_observations": len(valid),
        "findings": findings,
        "assessment": (
            "Human review recommended. Sample data does not confirm a flood."
        )
    }


def main():
    with DATA_FILE.open("r", encoding="utf-8-sig") as file:
        observations = json.load(file)

    print(json.dumps(analyze(observations), indent=2))


if __name__ == "__main__":
    main()
