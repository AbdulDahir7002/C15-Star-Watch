from datetime import datetime, timedelta

import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


def get_openmeteo():
    """Sets up caching and retries for openmeteo."""
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)


def get_dates() -> tuple[str, str]:
    """Return today, tomorrow date strings."""
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    return today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")


def make_requests(today: str, tomorrow: str, lat: float, long: float, openmeteo):
    """Make requests to open-meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ["temperature_2m", "precipitation_probability", "cloud_cover", "visibility"],
        "start_date": today,
        "end_date": tomorrow
    }
    responses = openmeteo.weather_api(url, params=params)
    return responses


def get_dataframe(hourly):
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["visibility"] = hourly_visibility

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    return hourly_dataframe


if __name__ == "__main__":
    openmeteo = get_openmeteo()
    today, tomorrow = get_dates()
    responses = make_requests(today, tomorrow, 51.8892, 0.9042, openmeteo)

    response = responses[0]

    hourly = response.Hourly()
    hourly_dataframe = get_dataframe(hourly)
    print(hourly_dataframe)
