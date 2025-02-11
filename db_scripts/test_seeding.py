# pylint: skip-file
import unittest
from unittest.mock import patch, MagicMock

from seeding import get_correct_location, get_locations

CITIES = ["London"]


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


class TestGetLocations(unittest.TestCase):
    @patch("seeding.get_correct_location")
    @patch("seeding.requests.get")
    def test_get_locations(self, mock_requests, mock_location):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [1]}

        mock_requests.return_value = mock_response

        mock_location.return_value = 1
        self.assertEqual(get_locations(CITIES), [1])

    @patch("seeding.get_correct_location")
    @patch("seeding.requests.get")
    def test_get_locations_returns_none(self, mock_requests, mock_location):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_requests.return_value = mock_response

        mock_location.return_value = None
        self.assertEqual(get_locations(CITIES), [])

    @patch("seeding.get_correct_location")
    @patch("seeding.requests.get")
    def test_get_locations_400_code(self, mock_requests, mock_location):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"results": []}

        mock_requests.return_value = mock_response
        mock_location.return_value = None
        self.assertEqual(get_locations(CITIES), [])


if __name__ == "__main__":
    unittest.main()
