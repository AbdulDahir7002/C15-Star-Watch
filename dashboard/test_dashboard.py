# pylint: skip-file
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime

import pandas as pd

from Page1 import get_weather_for_day, get_aurora_info, get_country, get_cities, get_days


class TestGetWeatherForDay(unittest.TestCase):
    def test_get_weather_for_day(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 2, 14.65, 86.0, 12345, '2025-02-14 06:00:00')]

        result = get_weather_for_day(date(2025, 2, 14), 'TestCity', mock_conn)

        expected_result = pd.DataFrame([['06'], [14.7],
                                        ['86'], ['12345']],
                                       index=['Time', 'Temperature',
                                              'Coverage', 'Visibility'],
                                       columns=[0])
        pd.testing.assert_frame_equal(result, expected_result)
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetAuroraInfo(unittest.TestCase):
    def test_get_aurora_info(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(0,
                                              datetime(2025, 2, 14, 8, 57, 32), False, False, 2)]
        result = get_aurora_info(2, mock_conn)
        expected_result = pd.DataFrame(
            {'Recording At': ['2025-02-14 08:57:32'],
             'Visible by Camera': ['False'],
             'Visible by Eye': ['False']})
        pd.testing.assert_frame_equal(result, expected_result)
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetCountry(unittest.TestCase):
    def test_get_country(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'Aberdeen')

        result = get_country('Aberdeen', mock_conn)
        self.assertEqual(result, 1)
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetCities(unittest.TestCase):
    def test_get_cities(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('Aberdeen',)]
        result = get_cities(mock_conn)
        self.assertEqual(['Aberdeen'], result)
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()


class TestGetDays(unittest.TestCase):
    @patch('Page1.date')
    def test_get_days(self, mock_date):
        mock_date.today.return_value = date(2025, 2, 14)
        result = get_days()
        expected_result = [
            date(2025, 2, 14),
            date(2025, 2, 15),
            date(2025, 2, 16),
            date(2025, 2, 17),
            date(2025, 2, 18),
            date(2025, 2, 19),
            date(2025, 2, 20),
            'Week'
        ]
        self.assertEqual(expected_result, result)


if __name__ == "__main__":
    unittest.main()
