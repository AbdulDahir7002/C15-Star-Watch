# pylint: skip-file
from os import environ

from unittest.mock import patch, MagicMock
import pytest
from dotenv import load_dotenv

from daily_etl import get_connection, get_locations, get_constellation_codes, post_location_get_moonphase, post_location_get_starchart, collate_data, upload_daily_data, handler, upload_constellation_urls

# load_dotenv()


@pytest.fixture()
def data_to_format():
    return {"code": "tes",
            "url":
                {"data":
                 {"imageUrl":
                  "www.test.com"
                  }}}


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("first_week.psycopg2.connect", return_value="mocked_conn")
def test_connection_made(mock_conn):
    """Tests that the connection function is called once"""
    get_connection()
    assert mock_conn.call_count == 1


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("first_week.psycopg2.connect", return_value="mocked_conn")
def test_city_format(mock_conn):
    """Tests that the query has the right format"""
    mock_connect = MagicMock()


@patch("first_week.psycopg2.connect")
def test_cursor_closes_locations(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    get_locations(mock_conn)

    mock_cursor.close.assert_called_once()


@patch("first_week.psycopg2.connect")
def test_cursor_closes_constellations(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    get_constellation_codes(mock_conn)

    mock_cursor.close.assert_called_once()


@patch("first_week.psycopg2.connect")
def test_cursor_closes_daily_upload(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    upload_daily_data(mock_conn)

    mock_cursor.close.assert_called_once()


@patch("first_week.psycopg2.connect")
def test_cursor_closes_constellation_upload(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    upload_constellation_urls(mock_conn)

    mock_cursor.close.assert_called_once()


@patch("first_week.psycopg2.connect")
def test_conn_closes(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()

    mock_connect.return_value = mock_conn

    handler(mock_conn)

    mock_conn.close.assert_called_once()


def test_format_for_db_update():
    """Tests the function processes an input properly"""
    pass
