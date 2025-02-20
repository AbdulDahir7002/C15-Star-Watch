# pylint: skip-file
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from seeding import get_correct_location, get_locations, get_date_objects, convert_peak_night_to_datetime

CITIES = ["London"]


class TestConvertPeakNightToDatetime(unittest.TestCase):
    @patch('seeding.datetime')
    def test_convert_peak_night_to_datetime(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2025, 2, 19)
        # Makes datetime constructor work still so mock_datetime doesn't break it.
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(
            *args, **kwargs)

        self.assertEqual(
            datetime(2025, 11, 16), convert_peak_night_to_datetime('Nov16-17'))


class TestGetCorrectLocation(unittest.TestCase):
    def test_get_correct_location(self):
        test_results = [
            {"country": "United Kingdom", "latitude": 1,
                "longitude": 1, "elevation": 1, "name": "testville", "admin1": "England"},
            {"country": "United States", "latitude": 0, "longitude": 0, "elevation": 0, "name": "test city", "admin1": "America"}]
        self.assertEqual(get_correct_location(
            test_results), ("testville", 1, 1, 1, 1))

    def test_get_correct_location_no_uk(self):
        test_results = [{"country": "United States", "latitude": 0,
                         "longitude": 0, "elevation": 0, "name": "test city"}]
        self.assertEqual(get_correct_location(test_results), None)

    def test_get_correct_location_scotland(self):
        test_results = [{"country": "United Kingdom", "latitude": 0,
                         "longitude": 0, "elevation": 0, "name": "test city", 'admin1': 'Scotland'}]
        self.assertEqual(get_correct_location(
            test_results), ("test city", 2, 0, 0, 0))

    def test_get_correct_location_wales(self):
        test_results = [{"country": "United Kingdom", "latitude": 0,
                         "longitude": 0, "elevation": 0, "name": "test city", 'admin1': 'Wales'}]
        self.assertEqual(get_correct_location(
            test_results), ("test city", 3, 0, 0, 0))

    def test_get_correct_location_northern_ireland(self):
        test_results = [{"country": "United Kingdom", "latitude": 0,
                         "longitude": 0, "elevation": 0, "name": "test city", 'admin1': 'Northern Ireland'}]
        self.assertEqual(get_correct_location(
            test_results), ("test city", 4, 0, 0, 0))


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


class TestGetDateObjects(unittest.TestCase):
    def test_get_date_objects(self):
        start_date = "October 2nd 2025"
        end_date = "October 3rd, 2025"
        start_object, end_object = get_date_objects(start_date, end_date)
        self.assertEqual(start_object, datetime(2025, 10, 2))
        self.assertEqual(end_object, datetime(2025, 10, 3))


if __name__ == "__main__":
    unittest.main()
