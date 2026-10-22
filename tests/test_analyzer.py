
import unittest
from src.analyzer import analyze


class TestTerraGuardAnalyzer(unittest.TestCase):

    def setUp(self):
        self.observations = [
            {
                "id": "OBS-001",
                "source": "Weather bulletin",
                "reported_at": "2026-10-22T08:00:00+05:30",
                "claim": "Heavy rainfall reported upstream",
                "rainfall_mm": 85,
            },
            {
                "id": "OBS-002",
                "source": "Water sensor A",
                "reported_at": "2026-10-22T08:15:00+05:30",
                "claim": "River water level is rising",
                "water_level_m": 4.2,
            },
            {
                "id": "OBS-003",
                "source": "Community report",
                "reported_at": "2026-10-22T08:20:00+05:30",
                "claim": "Water is entering two streets",
            },
            {
                "id": "OBS-004",
                "source": "Old report",
                "reported_at": "2026-10-21T18:00:00+05:30",
                "claim": "No flooding reported",
            },
            {
                "id": "OBS-005",
                "source": "Water sensor B",
                "reported_at": "2026-10-22T08:25:00+05:30",
                "claim": "Water level is stable",
                "water_level_m": 4.0,
            },
        ]

    def test_counts_all_observations(self):
        result = analyze(self.observations)
        self.assertEqual(result["observation_count"], 5)
        self.assertEqual(result["valid_timestamped_observations"], 5)

    def test_flags_stale_observation(self):
        result = analyze(self.observations)
        stale_ids = [
            finding["evidence_id"]
            for finding in result["findings"]
            if finding["type"] == "stale_evidence"
        ]
        self.assertIn("OBS-004", stale_ids)

    def test_flags_water_level_disagreement(self):
        result = analyze(self.observations)
        conflicts = [
            finding for finding in result["findings"]
            if finding["type"] == "water_level_disagreement"
        ]
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["measurements_m"], [4.2, 4.0])

    def test_does_not_claim_flood_confirmed(self):
        result = analyze(self.observations)
        self.assertIn("does not confirm a flood", result["assessment"])


if __name__ == "__main__":
    unittest.main()
