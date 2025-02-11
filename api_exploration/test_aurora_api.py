# pylint: skip-file
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from aurora_api import get_current_aurora_data

SAMPLE_AURORA_DATA = """
<current_status api_version="0.2.5">
<updated>
<datetime>2025-02-10T13:42:32+0000</datetime>
</updated>
<site_status project_id="project:AWN" site_id="site:AWN:SUM" site_url="http://aurorawatch-api.lancs.ac.uk/0.2.5/project/awn/sum.xml" status_id="green"/>
</current_status>
"""

SAMPLE_AURORA_OUTPUT = {
    'last_updated': '2025-02-10T13:42:32+0000', 'current_status': 'green'}


class TestAuroraAPI(unittest.TestCase):
    @patch('requests.get')
    def test_get_current_aurora_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = SAMPLE_AURORA_DATA
        mock_get.return_value = mock_response

        result = get_current_aurora_data()
        self.assertEqual(result, SAMPLE_AURORA_OUTPUT)
        mock_get.assert_called_once_with(
            "https://aurorawatch-api.lancs.ac.uk/0.2/status/current-status.xml")


if __name__ == "__main__":
    unittest.main()
