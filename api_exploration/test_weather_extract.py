# pylint: skip-file
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

from weather_extract import get_dates, convert_df_to_list, get_locations, clear_weather_table


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


class TestGetLocations(unittest.TestCase):
    def test_get_locations(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("test1", "test2"), ("test3", "test4")]

        result = get_locations(mock_conn)

        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM city;")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()
        self.assertEqual(
            result, [("test1", "test2"), ("test3", "test4")])


class TestClearWeatherTable(unittest.TestCase):
    def test_clear_weather_table(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor

        clear_weather_table(mock_conn)
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM weather_status;")
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
