# pylint: skip-file
import pytest
from dotenv import load_dotenv

from first_week import get_connection, get_locations, post_location_get_moonphase, post_location_get_starchart, collate_data
from unittest.mock import patch, MagicMock

load_dotenv()


@patch("extract_astro.psycopg2.connect", return_value="mocked_conn")
def test_connection_made(mock_conn):
    """Tests that the connection function is called once"""
    get_connection()
    assert mock_conn.call_count == 1


def test_city_format():
    """Tests that the query has the right format"""
    pass


@patch("extract_astro.psycopg2.connect")
def test_cursor_closes(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    get_locations(mock_conn)

    mock_cursor.close.assert_called_once()
