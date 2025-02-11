# pylint: skip-file
import unittest
from unittest.mock import patch

from seeding import get_correct_location


class TestGetCorrectLocation(unittest.TestCase):
    def test_get_correct_location(self):
        test_results = [
            {"country": "United Kingdom", "latitude": 1,
                "longitude": 1, "elevation": 1, "name": "testville"},
            {"country": "United States", "latitude": 0, "longitude": 0, "elevation": 0, "name": "test city"}]
        self.assertEqual(get_correct_location(
            test_results), ("testville", 1, 1, 1))

    def test_get_correct_location_no_uk(self):
        test_results = [{"country": "United States", "latitude": 0,
                         "longitude": 0, "elevation": 0, "name": "test city"}]
        self.assertEqual(get_correct_location(test_results), None)


if __name__ == "__main__":
    unittest.main()
