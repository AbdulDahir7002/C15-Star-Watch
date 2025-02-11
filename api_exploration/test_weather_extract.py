# pylint: skip-file
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
import pandas as pd

from weather_extract import get_dates, convert_df_to_list


class TestGetDates(unittest.TestCase):
    @patch('weather_extract.datetime')
    def test_get_dates(self, mock_datetime):
        mock_datetime.today.return_value = datetime(2025, 2, 10)
        today, tomorrow = get_dates()
        self.assertEqual(today, '2025-02-10')
        self.assertEqual(tomorrow, '2025-02-17')


class TestConvertDfToList(unittest.TestCase):
    def test_convert_df_to_list(self):
        test_df = pd.DataFrame(
            {'id': [1, 2], 'name': ['Alice', 'Bob']})
        self.assertEqual(convert_df_to_list(test_df),
                         [(1, 'Alice'), (2, 'Bob')])


if __name__ == "__main__":
    unittest.main()
