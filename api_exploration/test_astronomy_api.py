# pylint: skip-file
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from astronomy_api import get_body_locations, post_moon_phase, post_star_chart_url

SAMPLE_POSITIONS = {
    'data': {
        'dates': {
            'from': '2025-02-10T10:31:00.000Z', 'to': '2025-02-10T10:31:00.000Z'},
        'observer': {
            'location': {
                'longitude': -0.08,
                'latitude': 51.54,
                'elevation': 24.7}},
        'table': {
            'header': ['2025-02-10T10:31:00.000Z'],
            'rows': []
        }
    }
}

SAMPLE_MOON_PHASE = {
    'data':
    {
        'imageUrl': 'https://widgets.astronomyapi.com/moon-phase/generated/b49840b8c8c0036622ab9343a348b99c7c4f4acb6aad2bd5f50e3004becc815b.png'
    }
}

SAMPLE_STAR_CHART = {
    'data':
    {
        'imageUrl': 'https://widgets.astronomyapi.com/star-chart/generated/b7ed7c6e789c10d887c8f23ec942284a0f5057763c5d7f2e3836e285b1147102.png'
    }
}


class TestAstronomyAPI(unittest.TestCase):
    @patch('astronomy_api.requests.get')
    def test_get_body_locations(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_POSITIONS
        mock_get.return_value = mock_response
        HEADER = 'Basic'
        result = get_body_locations(HEADER, 51.54, -0.08, 21.7, "2025-02-11",
                                    "2025-02-11", "22:00:00")
        self.assertEqual(SAMPLE_POSITIONS, result)

    @patch('astronomy_api.requests.post')
    def test_post_moon_phase(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_MOON_PHASE
        mock_get.return_value = mock_response
        HEADER = 'Basic'
        result = post_moon_phase(HEADER, 33.775867, -84.39733, "2020-02-11")
        self.assertEqual(SAMPLE_MOON_PHASE, result)

    @patch('astronomy_api.requests.post')
    def test_get_star_chart_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = SAMPLE_STAR_CHART
        mock_get.return_value = mock_response
        HEADER = 'Basic'
        result = post_star_chart_url(
            HEADER, 33.775867,  -84.39733, "2020-02-11")
        self.assertEqual(SAMPLE_STAR_CHART, result)


if __name__ == "__main__":
    unittest.main()
