# pylint: skip-file
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

from weather_extract import get_dates, convert_df_to_list, get_locations, clear_weather_table, insert_into_db, get_weather_for_location, handle_locations


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


class TestInsertIntoDb(unittest.TestCase):
    @patch('weather_extract.execute_values')
    def test_insert_into_db(self, mock_execute_values):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        df = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
        insert_into_db(df, mock_conn)
        mock_conn.cursor.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetWeatherForLocation(unittest.TestCase):
    @patch("weather_extract.get_dataframe")
    @patch("weather_extract.make_requests")
    def test_get_weather_for_location(self, mock_make_requests, mock_get_dataframe):
        openmeteo = MagicMock()
        mock_response = MagicMock()
        mock_hourly = MagicMock()
        mock_response.Hourly.return_value = mock_hourly
        mock_make_requests.return_value = [mock_response]

        sample_df = pd.DataFrame({"temperature_2m": [10, 12, 14]})
        mock_get_dataframe.return_value = sample_df

        result_df = get_weather_for_location(
            "2025-02-10", "2025-02-17", 51.5, -0.12, openmeteo)
        mock_make_requests.assert_called_once_with(
            "2025-02-10", "2025-02-17", 51.5, -0.12, openmeteo)
        mock_get_dataframe.assert_called_once_with(mock_hourly)
        self.assertTrue(result_df.equals(sample_df))


class TestHandleLocations(unittest.TestCase):
    @patch("weather_extract.get_weather_for_location")
    def test_handle_locations(self, mock_get_weather):
        openmeteo = MagicMock()
        mock_get_weather.return_value = pd.DataFrame(
            {'id': [1, 2], 'name': ['Alice', 'Bob']})
        locations = [(0, 1, 2, 3, 4), (1, 2, 3, 4, 5)]
        df = handle_locations(locations, openmeteo, "2025-2-3", "2025-2-9")
        first = pd.Series({'id': 1, 'name': 'Alice', 'city_id': 1})
        last = pd.Series({'id': 2, 'name': 'Bob', 'city_id': 1})
        self.assertTrue(first.equals(df.iloc[0]))
        self.assertTrue(last.equals(df.iloc[-1]))


if __name__ == "__main__":
    unittest.main()
