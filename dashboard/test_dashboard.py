# pylint: skip-file
import unittest
from unittest.mock import patch, MagicMock
from datetime import date

import pandas as pd

from Page1 import get_weather_for_day


class TestGetWeatherForDay(unittest.TestCase):
    def test_get_weather_for_day(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 2, 14.65, 86.0, 12345, '2025-02-14 06:00:00')]

        result = get_weather_for_day(date(2025, 2, 14), 'TestCity', mock_conn)

        expected_result = pd.DataFrame([[6], [14.7],
                                        ['86'], ['12345']],
                                       index=['Time', 'Temperature',
                                              'Coverage', 'Visibility'],
                                       columns=[0])
        pd.testing.assert_frame_equal(result, expected_result)
        self.assertTrue(mock_cursor.execute.called)
        self.assertTrue(mock_cursor.fetchall.called)


if __name__ == "__main__":
    unittest.main()
