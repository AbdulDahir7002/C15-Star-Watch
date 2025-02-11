"""Script to extract weather information from open-meteo."""
from datetime import datetime, timedelta
from os import environ as ENV

import openmeteo_requests

import requests_cache
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from retry_requests import retry
from dotenv import load_dotenv


def get_connection():
    """Returns psycopg2 connection object."""
    connection = psycopg2.connect(
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
    )
    return connection


def get_openmeteo():
    """Sets up caching and retries for openmeteo."""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)


def get_dates() -> tuple[str, str]:
    """Return today, a week from now date strings."""
    today = datetime.today()
    week_away = today + timedelta(days=7)
    return today.strftime("%Y-%m-%d"), week_away.strftime("%Y-%m-%d")


def make_requests(today: str, week_away: str, lat: float, long: float, openmeteo):
    """Make requests to open-meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ["temperature_2m", "cloud_cover", "visibility"],
        "start_date": today,
        "end_date": week_away
    }
    responses = openmeteo.weather_api(url, params=params)
    return responses


def get_dataframe(hourly) -> pd.DataFrame:
    """Returns dataframe of weather."""
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["visibility"] = hourly_visibility

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    return hourly_dataframe


def get_weather_for_location(today: str, week_away: str,
                             lat: float, long: float,
                             openmeteo
                             ) -> pd.DataFrame:
    """Returns dataframe of weather at the given location."""
    responses = make_requests(today, week_away, lat, long, openmeteo)
    response = responses[0]
    hourly = response.Hourly()
    hourly_dataframe = get_dataframe(hourly)
    return hourly_dataframe


def get_locations(connection) -> list:
    """Fetches list of locations from the database."""
    curs = connection.cursor()
    curs.execute("SELECT * FROM city;")
    results = curs.fetchall()
    curs.close()
    return results


def handle_locations(locations: list, openmeteo, today_str: str, week_str: str) -> pd.DataFrame:
    """Makes requests for every location in the list."""
    dataframes = []

    for location in locations:
        df = get_weather_for_location(
            today_str, week_str, location[3], location[4], openmeteo)
        df['city_id'] = pd.Series([location[0]]*192)
        dataframes.append(df)

    all_weather_df = pd.concat(dataframes, ignore_index=True)
    return all_weather_df


def clear_weather_table(connection) -> None:
    """Empties weather table for new data."""
    curs = connection.cursor()
    curs.execute("DELETE FROM weather_status;")
    connection.commit()
    curs.close()


def insert_into_db(all_weather_df: pd.DataFrame, connection) -> None:
    """Inserts the weather into the database."""
    tuple_list = [tuple(row) for row in all_weather_df.itertuples(index=False)]
    curs = connection.cursor()
    query = """
            INSERT INTO weather_status (status_at, temperature, coverage, visibility, city_id)
            VALUES %s
            """
    execute_values(curs, query, tuple_list)
    connection.commit()
    curs.close()


def lambda_handler(event, context):
    """Function for lambda handler."""


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    open_meteo = get_openmeteo()
    locations = get_locations(conn)
    today_str, week_str = get_dates()
    data = handle_locations(locations, open_meteo, today_str, week_str)
    clear_weather_table(conn)
    insert_into_db(data, conn)
    conn.close()
