import unittest

from src.zetaris_connector import (
    DATA_SOURCE_LABEL,
    load_sample_flood_evidence,
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


if __name__ == "__main__":
    unittest.main()
