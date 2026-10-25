
import unittest
from unittest.mock import Mock, patch

from src.zetaris_connector import (
    DATA_SOURCE_LABEL,
    WEATHER_TABLE,
    ZetarisConnectionError,
    _fetchall_dicts,
    fetch_ny_taxi_weather,
    load_sample_flood_evidence,
    validate_query_limit,
)


class TestZetarisConnector(unittest.TestCase):
    def test_load_sample_flood_evidence_returns_records(self):
        records = load_sample_flood_evidence()

        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)

    def test_sample_evidence_records_are_dictionaries(self):
        records = load_sample_flood_evidence()

        for record in records:
            self.assertIsInstance(record, dict)

    def test_sample_evidence_has_source_label(self):
        records = load_sample_flood_evidence()

        self.assertIn("LOCAL SAMPLE", DATA_SOURCE_LABEL.upper())
        self.assertIn("NOT LIVE ZETARIS", DATA_SOURCE_LABEL.upper())

        for record in records:
            self.assertIn("source", record)
            self.assertTrue(record["source"])

    def test_data_source_label_explicitly_identifies_local_sample_data(self):
        self.assertIn("LOCAL SAMPLE DATA", DATA_SOURCE_LABEL.upper())
        self.assertIn("NOT LIVE ZETARIS", DATA_SOURCE_LABEL.upper())

    def test_validate_query_limit_accepts_valid_integer(self):
        self.assertEqual(validate_query_limit(5), 5)

    def test_validate_query_limit_rejects_invalid_values(self):
        invalid_values = [0, -1, 1.5, True, "abc"]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_query_limit(value)

    def test_validate_query_limit_accepts_numeric_string(self):
        self.assertEqual(validate_query_limit("10"), 10)

    def test_validate_query_limit_uses_default_when_none(self):
        self.assertEqual(validate_query_limit(None, default=5), 5)

    def test_fetchall_dicts_converts_rows_to_dictionaries(self):
        cursor = Mock()
        cursor.description = [
            ("id",),
            ("location",),
        ]
        cursor.fetchall.return_value = [
            (1, "Newark"),
            (2, "Jamaica Bay"),
        ]

        records = _fetchall_dicts(cursor)

        self.assertEqual(
            records,
            [
                {"id": 1, "location": "Newark"},
                {"id": 2, "location": "Jamaica Bay"},
            ],
        )

    @patch("src.zetaris_connector.connect_zetaris")
    def test_fetch_weather_returns_source_metadata(self, mock_connect):
        cursor = Mock()
        cursor.description = [
            ("zone_id",),
            ("precipitation",),
        ]
        cursor.fetchall.return_value = [
            (1, "0.5"),
            (2, "1.2"),
        ]

        connection = Mock()
        connection.cursor.return_value = cursor
        mock_connect.return_value = connection

        records = fetch_ny_taxi_weather(limit=2, config=Mock())

        self.assertEqual(len(records), 2)

        for record in records:
            self.assertEqual(record["_source_system"], "zetaris_jdbc")
            self.assertEqual(record["_source_table"], WEATHER_TABLE)
            self.assertEqual(record["_query_limit"], 2)
            self.assertIn("zone_id", record)
            self.assertIn("precipitation", record)

        self.assertEqual(
            cursor.execute.call_args.args[0],
            f"SELECT * FROM {WEATHER_TABLE} LIMIT 2",
        )
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    @patch("src.zetaris_connector.connect_zetaris")
    def test_connection_closes_if_cursor_close_raises(self, mock_connect):
        cursor = Mock()
        cursor.description = [
            ("zone_id",),
            ("precipitation",),
        ]
        cursor.fetchall.return_value = [(1, "0.5")]
        cursor.close.side_effect = RuntimeError("cursor close failed")

        connection = Mock()
        connection.cursor.return_value = cursor
        mock_connect.return_value = connection

        with self.assertRaises(RuntimeError):
            fetch_ny_taxi_weather(limit=1, config=Mock())

        connection.close.assert_called_once()

    @patch("src.zetaris_connector.connect_zetaris")
    def test_query_error_is_preserved_when_cleanup_also_fails(
        self, mock_connect
    ):
        query_error = RuntimeError("original query failed")
        cursor = Mock()
        cursor.execute.side_effect = query_error
        cursor.close.side_effect = RuntimeError("cursor cleanup failed")

        connection = Mock()
        connection.cursor.return_value = cursor
        connection.close.side_effect = RuntimeError(
            "connection cleanup failed"
        )
        mock_connect.return_value = connection

        with self.assertRaises(ZetarisConnectionError) as context:
            fetch_ny_taxi_weather(limit=1, config=Mock())

        # The public connection error must retain the original query failure.
        self.assertIs(context.exception.__cause__, query_error)
        cursor.close.assert_called_once()
        connection.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
