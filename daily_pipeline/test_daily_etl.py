# pylint: skip-file
# Replace with your actual module name
import requests_mock
from os import environ

from unittest.mock import patch, MagicMock
import pytest

from daily_etl import get_connection, get_locations, get_constellation_codes, post_location_get_moonphase, post_location_get_starchart, upload_daily_data, handler, upload_constellation_urls, get_sunrise_and_set_times


@pytest.fixture()
def data_to_format():
    """Data input that can be used"""
    return {"code": "tes",
            "url":
                {"data":
                 {"imageUrl":
                  "www.test.com"
                  }}}


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("daily_etl.psycopg2.connect", return_value="mocked_conn")
def test_connection_made(mock_conn):
    """Tests that the connection function is called once"""
    get_connection()
    assert mock_conn.call_count == 1


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("daily_etl.psycopg2.connect")
def test_cursor_closes_locations(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    get_locations(mock_conn)

    mock_cursor.close.assert_called_once()


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("daily_etl.psycopg2.connect")
def test_cursor_closes_constellations(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    get_constellation_codes(mock_conn)

    mock_cursor.close.assert_called_once()


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("daily_etl.psycopg2.connect")
def test_cursor_closes_daily_upload(mock_connect):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor

    mock_connect.return_value = mock_conn

    upload_daily_data(mock_conn, data_to_format)

    mock_cursor.close.assert_called_once()


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT"})
@patch("daily_etl.psycopg2.connect")
def test_cursor_closes_constellation_upload(mock_connect, data_to_format):
    """Tests the cursor is closed"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    data_to_format["new_url"] = "www.new_url.com"
    mock_connect.return_value = mock_conn
    upload_constellation_urls(
        mock_conn, [data_to_format])

    mock_cursor.close.assert_called_once()


def test_post_location_get_moonphase(requests_mock):
    """The the API response is handled correctly"""
    header = "Basic test_token"
    lat = 45.101
    long = 0.545
    date_to_query = "2025-02-21"

    mock_url = "https://api.astronomyapi.com/api/v2/studio/moon-phase"
    mock_response = {
        "data": {
            "imageUrl": "www.moonphase-test.com"
        }
    }

    requests_mock.post(mock_url, json=mock_response)

    result = post_location_get_moonphase(header, lat, long, date_to_query)
    last_request = requests_mock.request_history[0]

    assert result == "www.moonphase-test.com"
    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert last_request.method == "POST"
    assert last_request.headers["Authorization"] == header


def test_post_location_get_starchart(requests_mock):
    """The the API response is handled correctly"""
    header = "Basic test_token"
    lat = 45.101
    long = 0.545
    date_to_query = "2025-02-21"

    mock_url = "https://api.astronomyapi.com/api/v2/studio/star-chart"
    mock_response = {
        "data": {
            "imageUrl": "www.starchart-test.com"
        }
    }

    requests_mock.post(mock_url, json=mock_response)

    result = post_location_get_starchart(header, lat, long, date_to_query)
    last_request = requests_mock.request_history[0]

    assert result == "www.starchart-test.com"
    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert last_request.method == "POST"
    assert last_request.headers["Authorization"] == header


def test_get_sunrise_sunset_times(requests_mock):
    """The the API response is handled correctly"""
    lat = 45.101
    long = 0.545
    date_to_query = "2025-02-21"

    mock_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=sunrise,sunset&timezone=auto&start_date={date_to_query}&end_date={date_to_query}"
    mock_response = {
        "daily": {
            "sunrise": ["2025-02-21T07:35"], "sunset": ["2025-02-21T17:35"]
        }
    }

    requests_mock.get(mock_url, json=mock_response)

    result1, result2 = get_sunrise_and_set_times(lat, long, date_to_query)
    last_request = requests_mock.request_history[0]

    assert result1 != result2
    assert type(result1) == str
    assert type(result2) == str
    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert last_request.method == "GET"


@patch.dict(environ, {"DB_HOST": "HOST", "DB_USERNAME": "USERNAME", "DB_NAME": "NAME", "DB_PASSWORD": "PASSWORD", "DB_PORT": "PORT", "ASTRONOMY_BASIC_AUTH_KEY": "ASTRO_KEY"})
@patch("daily_etl.psycopg2.connect")
def test_conn_closes(mock_connect):
    """Tests the connection is closed"""
    mock_conn = MagicMock()
    event = None
    context = None
    mock_connect.return_value = mock_conn

    handler(event, context)

    mock_conn.close.assert_called_once()


def test_format_for_db_update():
    """Tests the function processes an input properly"""
    pass
