
import unittest
from unittest.mock import Mock, patch

from src.zetaris_connector import (
    DATA_SOURCE_LABEL,
    _fetchall_dicts,
    load_sample_flood_evidence,
    validate_query_limit,
)


class TestZetarisConnector(unittest.TestCase):

    def test_loads_five_sample_records(self):
        records = load_sample_flood_evidence()
        self.assertEqual(len(records), 5)

    def test_records_are_dictionaries(self):
        records = load_sample_flood_evidence()
        self.assertTrue(all(isinstance(record, dict) for record in records))

    def test_data_is_clearly_labeled_as_sample(self):
        self.assertIn("LOCAL SAMPLE DATA", DATA_SOURCE_LABEL)
        self.assertIn("not live Zetaris", DATA_SOURCE_LABEL)

    def test_valid_query_limits(self):
        self.assertEqual(validate_query_limit(1), 1)
        self.assertEqual(validate_query_limit(5), 5)
        self.assertEqual(validate_query_limit(100), 100)

    def test_rejects_invalid_query_limits(self):
        for limit in (0, -1, 101, True, "abc", ""):
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    validate_query_limit(limit)

    def test_accepts_string_and_default_query_limits(self):
        self.assertEqual(validate_query_limit("5"), 5)
        self.assertEqual(validate_query_limit(None), 5)

    def test_fetchall_dicts_preserves_column_names_and_values(self):
        cursor = Mock()
        cursor.description = [
            ("location",),
            ("precipitation",),
        ]
        cursor.fetchall.return_value = [
            ("Riverbend", "1.2"),
            ("Northbank", "0.5"),
        ]

        records = _fetchall_dicts(cursor)

        self.assertEqual(
            records,
            [
                {"location": "Riverbend", "precipitation": "1.2"},
                {"location": "Northbank", "precipitation": "0.5"},
            ],
        )

    @patch("src.zetaris_connector.connect_zetaris")
    def test_fetch_weather_returns_source_metadata(self, mock_connect):
        from src.zetaris_connector import fetch_ny_taxi_weather

        cursor = Mock()
        cursor.description = [
            ("location",),
            ("precipitation",),
        ]
        cursor.fetchall.return_value = [("Newark Airport", "1.2")]

        connection = Mock()
        connection.cursor.return_value = cursor
        mock_connect.return_value = connection

        records = fetch_ny_taxi_weather(limit=1, config=Mock())

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["location"], "Newark Airport")
        self.assertEqual(records[0]["precipitation"], "1.2")
        self.assertEqual(records[0]["_source_system"], "zetaris_jdbc")
        self.assertEqual(records[0]["_source_table"], "NY_TAXI.weather_data")
        self.assertEqual(records[0]["_query_limit"], 1)

        cursor.close.assert_called_once()
        connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
