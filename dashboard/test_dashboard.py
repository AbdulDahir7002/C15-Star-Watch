# pylint: skip-file
import unittest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import os

import pandas as pd

from Page1 import get_weather_for_day, get_aurora_info, get_country, get_cities, get_days, get_emoji_for_weather, get_meteor_showers_for_day, get_stargazing_status_for_day, get_weather_for_week, get_lat_and_long, get_constellation_code, get_constellations, get_stargazing_status_for_week, post_location_get_starchart
from Home import get_nasa_apod


class TestPostLocationGetStarChart(unittest.TestCase):
    @patch('Page1.requests')
    def test_post_location_get_starchart(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {'data': {'imageUrl': 'Test'}}
        mock_requests.post.return_value = mock_response
        self.assertEqual(
            'Test', post_location_get_starchart('', '', '', '', ''))


class TestGetNasaApod(unittest.TestCase):
    @patch.dict(os.environ, {"NASA_APOD_KEY": "test_api_key"})
    @patch('Home.requests.get')
    def test_get_nasa_apod(self, mock_get):
        mock_response = {
            'explanation': 'This is a test explanation',
            'title': 'Test APOD',
            'url': 'https://example.com/image.jpg',
            'date': '2025-02-18'
        }
        mock_get.return_value.json.return_value = mock_response

        result = get_nasa_apod()

        self.assertEqual(result, mock_response)
        mock_get.assert_called_once()


class TestGetWeatherForDay(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_weather_for_day(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 2, 14.65, 86.0, 12345, '2025-02-14 06:00:00')]

        result = get_weather_for_day(date(2025, 2, 14), 'TestCity')

        expected_result = pd.DataFrame([['06'], [14.7],
                                        ['86'], ['12345']],
                                       index=['Time', 'Temperature',
                                              'Coverage', 'Visibility'],
                                       columns=[0])
        pd.testing.assert_frame_equal(result, expected_result)
        mock_conn.cursor.assert_called_once()


class TestGetWeatherForWeek(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_weather_for_week(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 2, 14.65, 86.0, 12345, '2025-02-14 06:00:00')]

        result = get_weather_for_week('TestCity')

        expected_result = pd.DataFrame([('2025-02-14 06:00:00', 14.7,
                                        float(86), float(12345))],
                                       columns=['Time', 'Temperature',
                                                'Coverage', 'Visibility'])
        pd.testing.assert_frame_equal(result, expected_result)
        mock_conn.cursor.assert_called_once()


class TestGetStargazingForWeek(unittest.TestCase):
    @patch('Page1.date')
    @patch('Page1.get_connection')
    def test_get_stargazing_for_week(self, mock_get_connection, mock_date):
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_date.today.return_value = date(2025, 2, 16)
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs
        mock_curs.fetchall.return_value = [
            (1, 1, 1, 1, 1, 'URL', 'URL', 'Testcity')
        ]
        self.assertEqual(
            [
                (1, 1, 1, 1, 1, 'URL', 'URL', 'Testcity')
            ], get_stargazing_status_for_week('Testcity'))
        mock_conn.cursor.assert_called_once()


class TestGetAuroraInfo(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_aurora_info(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(0,
                                              datetime(2025, 2, 14, 8, 57, 32), False, False, 2)]
        result = get_aurora_info(2)
        expected_result = pd.DataFrame(
            {'Recording At': ['2025-02-14 08:57:32'],
             'Visible by Camera': ['False'],
             'Visible by Eye': ['False']})
        pd.testing.assert_frame_equal(result, expected_result)
        mock_conn.cursor.assert_called_once()


class TestGetCountry(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_country(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'Aberdeen')

        result = get_country('Aberdeen')
        self.assertEqual(result, 1)
        mock_conn.cursor.assert_called_once()


class TestGetLatAndLong(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_lat_and_long(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(10, 13)]

        lat, long = get_lat_and_long('Aberdeen')
        self.assertEqual(lat, 10)
        self.assertEqual(long, 13)
        mock_conn.cursor.assert_called_once()


class TestGetConstellationCode(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_constellation_code(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [('ori')]

        result = get_constellation_code('Orion')
        self.assertEqual(result, 'ori')
        mock_conn.cursor.assert_called_once()


class TestGetCities(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_cities(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('Aberdeen',)]
        result = get_cities()
        self.assertEqual(['Aberdeen'], result)


class TestGetConstellations(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_constellations(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('Orion', 'ori')]
        result = get_constellations()
        self.assertEqual(['Orion'], result)
        mock_conn.cursor.assert_called_once()


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

    @patch('Page1.date')
    def test_get_days_eom(self, mock_date):
        mock_date.today.return_value = date(2025, 2, 26)
        result = get_days()
        expected_result = [
            date(2025, 2, 26),
            date(2025, 2, 27),
            date(2025, 2, 28),
            date(2025, 3, 1),
            date(2025, 3, 2),
            date(2025, 3, 3),
            date(2025, 3, 4),
            'Week'
        ]
        self.assertEqual(expected_result, result)

    @patch('Page1.date')
    def test_get_days_eoy(self, mock_date):
        mock_date.today.return_value = date(2025, 12, 27)
        result = get_days()
        expected_result = [
            date(2025, 12, 27),
            date(2025, 12, 28),
            date(2025, 12, 29),
            date(2025, 12, 30),
            date(2025, 12, 31),
            date(2026, 1, 1),
            date(2026, 1, 2),
            'Week'
        ]
        self.assertEqual(expected_result, result)


class TestGetEmojiForWeather(unittest.TestCase):
    def test_get_emoji_for_weather_cloud(self):
        weather = pd.DataFrame([['06'], [14.7],
                                ['86'], ['12345']],
                               index=['Time', 'Temperature',
                                      'Coverage', 'Visibility'],
                               columns=[0])
        self.assertEqual('&#x2601;', get_emoji_for_weather(weather))

    def test_get_emoji_for_weather_slightsun(self):
        weather = pd.DataFrame([['06'], [14.7],
                                ['84'], ['12345']],
                               index=['Time', 'Temperature',
                                      'Coverage', 'Visibility'],
                               columns=[0])
        self.assertEqual('&#x26C5;', get_emoji_for_weather(weather))

    def test_get_emoji_for_weather_somesun(self):
        weather = pd.DataFrame([['06'], [14.7],
                                ['64'], ['12345']],
                               index=['Time', 'Temperature',
                                      'Coverage', 'Visibility'],
                               columns=[0])
        self.assertEqual('&#x1F324;', get_emoji_for_weather(weather))

    def test_get_emoji_for_weather_sunny(self):
        weather = pd.DataFrame([['06'], [14.7],
                                ['29'], ['12345']],
                               index=['Time', 'Temperature',
                                      'Coverage', 'Visibility'],
                               columns=[0])
        self.assertEqual('&#9728;', get_emoji_for_weather(weather))


class TestGetMeteorShowersPerDay(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_meteor_shower_per_day_none(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs
        mock_curs.fetchall.return_value = []
        self.assertEqual(None, get_meteor_showers_for_day('1'))

    @patch('Page1.get_connection')
    def test_get_meteor_shower_per_day(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs
        mock_curs.fetchall.return_value = [(1, 'name', 'start', 'end', 'peak')]

        result = get_meteor_showers_for_day('1')
        expected_result = pd.DataFrame({'id': [1],
                                        'Name': ['name'],
                                        'Start Date': ['start'],
                                        'End Date': ['end'],
                                        'Peak Date': ['peak']})
        pd.testing.assert_frame_equal(result, expected_result)


class TestGetStargazingStatusForDay(unittest.TestCase):
    @patch('Page1.get_connection')
    def test_get_stargazing_status_for_day(self, mock_get_connection):
        mock_conn = MagicMock()
        mock_curs = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_curs
        mock_curs.fetchone.return_value = (1, 2, 3)
        self.assertEqual(
            (1, 2, 3), get_stargazing_status_for_day('1', '1'))
        mock_conn.cursor.assert_called_once()


if __name__ == "__main__":
    unittest.main()
