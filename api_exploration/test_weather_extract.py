# pylint: skip-file
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from weather_extract import get_dates


class TestGetDates(unittest.TestCase):
    @patch('datetime.datetime')
    def test_get_dates(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2025, 2, 10)
        today, tomorrow = get_dates()
        self.assertEqual(today, '2025-02-10')
        self.assertEqual(tomorrow, '2025-02-11')


if __name__ == "__main__":
    unittest.main()
