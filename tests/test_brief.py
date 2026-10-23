import unittest

from src.analyzer import analyze
from src.brief import build_incident_brief


class TestIncidentBrief(unittest.TestCase):

    def setUp(self):
        self.observations = [
            {
                "id": "OBS-001",
                "location": "Riverbend Village",
                "source": "Sample weather bulletin",
                "reported_at": "2026-10-22T08:00:00+05:30",
                "claim": "Heavy rainfall reported upstream",
                "rainfall_mm": 85,
                "status": "sample_data",
            },
            {
                "id": "OBS-002",
                "source": "Sample water-level sensor",
                "reported_at": "2026-10-22T08:15:00+05:30",
                "claim": "River water level is rising",
                "water_level_m": 4.2,
                "status": "sample_data",
            },
            {
                "id": "OBS-004",
                "source": "Sample old situation report",
                "reported_at": "2026-10-21T18:00:00+05:30",
                "claim": "No flooding reported",
                "status": "sample_data",
            },
            {
                "id": "OBS-005",
                "source": "Sample sensor feed",
                "reported_at": "2026-10-22T08:25:00+05:30",
                "claim": "Water level is stable",
                "water_level_m": 4.0,
                "status": "sample_data",
            },
        ]
        self.analysis = analyze(self.observations)
        self.brief = build_incident_brief(self.observations, self.analysis)

    def test_brief_labels_simulated_sample_data(self):
        self.assertIn("SIMULATED SAMPLE DATA", self.brief)

    def test_brief_does_not_confirm_a_flood(self):
        lower = self.brief.lower()
        self.assertIn("does not confirm a flood", lower)

    def test_brief_includes_assessment_from_analyzer(self):
        self.assertIn(self.analysis["assessment"], self.brief)

    def test_brief_lists_evidence_ids(self):
        self.assertIn("OBS-001", self.brief)
        self.assertIn("OBS-004", self.brief)


if __name__ == "__main__":
    unittest.main()
