"""Tests for weekly report generator script."""

import os
import pytest
from pandas.testing import assert_frame_equal
import pandas as pd
from unittest.mock import patch, MagicMock
from weekly_report_generator import get_connection, get_all_cities, get_meteor_peak, get_starting_meteors, get_ending_meteors, combine_meteor_info, average_coverage_graph, average_visibility_graph, sunrise_set_df, highest_coverage_day, best_stargazing_day


@patch.dict(os.environ, {"DB_HOST": "host", "DB_USERNAME": "user", "DB_PASSWORD": "password", "DB_NAME": "name", "DB_PORT": "390"})
@patch("weekly_report_generator.psycopg2.connect")
def test_connection_is_called(fake_connection):
    get_connection()
    fake_connection.assert_called()


@pytest.mark.parametrize("inp, out", [([{"city_name": "London"}], ["London"]), ([{"city_name": "London"}, {"city_name": "Londonderry"}], ["London", "Londonderry"]), ([{"city_name": "London"}, {"city_name": "London"}, {"city_name": "London"}], ["London", "London", "London"])])
def test_get_all_cities(inp, out):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = inp
    assert get_all_cities(conn) == out


@pytest.mark.parametrize("inp, out", [([{"meteor_shower_name": "Meteor", "days": 2}], [{"shower_name": "Meteor", "days": "will reach it's peak in 2 days."}])])
def test_get_meteor_peak_format(inp, out):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = inp
    assert get_meteor_peak(conn) == out


@pytest.mark.parametrize("inp, out", [([{"meteor_shower_name": "Meteor", "days": 2}], [{"shower_name": "Meteor", "days": "will start in 2 days."}])])
def test_get_starting_meteors_format(inp, out):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = inp
    assert get_starting_meteors(conn) == out


@pytest.mark.parametrize("inp, out", [([{"meteor_shower_name": "Meteor", "days": 2}], [{"shower_name": "Meteor", "days": "will end in 2 days."}])])
def test_get_ending_meteors_format(inp, out):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = inp
    assert get_ending_meteors(conn) == out


@pytest.mark.parametrize("peak, start, end, out", [(["peak"], ["start"], ["end"], ["peak", "start", "end"]), ([1], [2], [3], [1, 2, 3])])
def test_combine_meteor_info(peak, start, end, out):
    assert combine_meteor_info(peak, start, end) == out


@patch("weekly_report_generator.alt.Chart.save")
def test_average_coverage_graph(fake_save):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = {}
    average_coverage_graph(conn, "city")
    fake_save.assert_called()


@patch("weekly_report_generator.alt.Chart.save")
def test_average_visibility_graph(fake_save):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = {}
    average_visibility_graph(conn, "city")
    fake_save.assert_called()


def test_sunrise_set_df_format():
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = pd.DataFrame({"weekday": [
        "mon"], "sunrise": ["12:12:00"], "sunset": ["12:12:00"]})
    return_df = pd.DataFrame({"weekday": ["mon"], "sunrise": [
                             "12:12"], "sunset": ["12:12"]}).set_index("weekday").T
    assert_frame_equal(return_df, sunrise_set_df(conn, "city"))


@pytest.mark.parametrize("inp, out", [([], "No data"), ([{"date": "Tue"}], "Tue"), ([{"date": "Wed", "visibility": 100}], "Wed")])
def test_highest_coverage_day(inp, out):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchall.return_value = inp
    assert highest_coverage_day(conn, "city") == out


@pytest.mark.parametrize("inp, out", [(None, {"day": "", "visibility": "", "coverage": ""}), ({"date": "Tue", "visibility": 200, "coverage": 290}, {"day": "Tue", "visibility": 200, "coverage": 290})])
def test_best_stargazing_day(inp, out):
    conn = MagicMock()
    cur = conn.cursor()
    cur.fetchone.return_value = inp
    assert best_stargazing_day(conn, "city") == out
