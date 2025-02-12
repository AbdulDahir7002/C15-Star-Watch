# pylint: skip-file
import unittest
from unittest.mock import patch, MagicMock

from aurora_status import get_status_per_country, get_current_aurora_data

SAMPLE_STATUS_GREEN = {'last_updated': '2025-02-12T10:24:32+0000',
                       'current_status': 'green'}

SAMPLE_STATUS_YELLOW = {'last_updated': '2025-02-12T10:24:32+0000',
                        'current_status': 'yellow'}

SAMPLE_STATUS_RED = {'last_updated': '2025-02-12T10:24:32+0000',
                     'current_status': 'red'}


SAMPLE_COUNTRY = {'England': 1,
                  'Scotland': 2,
                  'Wales': 3,
                  'Northern Ireland': 4}

SAMPLE_OUTPUT_GREEN = [(2, '2025-02-12T10:24:32+0000', False, False),
                       (1, '2025-02-12T10:24:32+0000', False, False),
                       (3, '2025-02-12T10:24:32+0000', False, False),
                       (4, '2025-02-12T10:24:32+0000', False, False)]


SAMPLE_OUTPUT_YELLOW = [(2, '2025-02-12T10:24:32+0000', True, True),
                        (1, '2025-02-12T10:24:32+0000', True, False),
                        (3, '2025-02-12T10:24:32+0000', False, False),
                        (4, '2025-02-12T10:24:32+0000', True, False)]

SAMPLE_AURORA_XML_GREEN = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<!DOCTYPE current_status PUBLIC "-//AuroraWatch-API//DTD REST 0.2.5//EN" "">
<current_status api_version="0.2.5"><updated><datetime>2025-02-12T10:24:32+0000</datetime></updated><site_status project_id="" site_id="" site_url="" status_id="green"/></current_status>
"""

SAMPLE_AURORA_XML_RED = """<?xml version='1.0' encoding='UTF-8' standalone='yes'?>
<!DOCTYPE current_status PUBLIC "-//AuroraWatch-API//DTD REST 0.2.5//EN" "">
<current_status api_version="0.2.5"><updated><datetime>2025-02-12T10:24:32+0000</datetime></updated><site_status project_id="" site_id="" site_url="" status_id="red"/></current_status>
"""


class TestAurora_status(unittest.TestCase):
    def test_get_status_per_country(self):
        status_list_green = get_status_per_country(
            SAMPLE_STATUS_GREEN, SAMPLE_COUNTRY)
        self.assertEqual(status_list_green, SAMPLE_OUTPUT_GREEN)

        status_list_yellow = get_status_per_country(
            SAMPLE_STATUS_YELLOW, SAMPLE_COUNTRY)
        self.assertEqual(status_list_yellow, SAMPLE_OUTPUT_YELLOW)

    @patch("aurora_status.requests.get")
    def test_get_current_aurora_data_green(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_AURORA_XML_GREEN

        mock_get.return_value = mock_response
        response = get_current_aurora_data()
        self.assertEqual(response, SAMPLE_STATUS_GREEN)
        mock_get.assert_called_once_with(
            "https://aurorawatch-api.lancs.ac.uk/0.2/status/current-status.xml", timeout=10)

    @patch("aurora_status.requests.get")
    def test_get_current_aurora_data_red(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_AURORA_XML_RED

        mock_get.return_value = mock_response
        response = get_current_aurora_data()
        self.assertEqual(response, SAMPLE_STATUS_RED)
        mock_get.assert_called_once_with(
            "https://aurorawatch-api.lancs.ac.uk/0.2/status/current-status.xml", timeout=10)
