"""Runs the pipeline for 8 days from current date, to keep up with forecast"""
from os import environ as ENV
from datetime import datetime, date, timedelta

import requests
from dotenv import load_dotenv

from extract_astro import post_location_get_starchart, post_location_get_moonphase, get_connection, get_locations, format_tasks


def post_location_get_starchart(header: str, lat: float, long: float, date_to_query: str):
    """returns the url of a star chart for specific coordinates"""
    body = {
        "style": "default",
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": date_to_query
        },
        "view": {
            "type": "constellation",
            "parameters": {
                "constellation": "ori"
            }
        }
    }

    response = requests.post(
        "https://api.astronomyapi.com/api/v2/studio/star-chart",
        headers={'Authorization': header},
        json=body,
        timeout=60
    )

    return response.json()['data']['imageUrl']


def post_location_get_moonphase(header: str, lat: float, long: float, date_to_query: str):
    """returns the url of a star chart for specific coordinates"""
    body = {
        "format": "png",
        "style": {
            "moonStyle": "sketch",
            "backgroundStyle": "stars",
            "backgroundColor": "red",
            "headingColor": "white",
            "textColor": "red"
        },
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": date_to_query
        },
        "view": {
            "type": "portrait-simple",
            "orientation": "south-up"
        }
    }

    response = requests.post(
        "https://api.astronomyapi.com/api/v2/studio/moon-phase",
        headers={'Authorization': header},
        json=body,
        timeout=60
    )
    return response.json()['data']['imageUrl']


def get_sunrise_and_set_times(lat: float, long: float, date_to_query: str):
    """Call from the open meteo API to get the daily sunrise and sunset times"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=sunrise,sunset&timezone=auto&start_date={date_to_query}&end_date={date_to_query}"
    response = requests.get(url)
    data = response.json()
    sunrise = data['daily']['sunrise'][0]
    sunset = data['daily']['sunset'][0]

    return sunrise, sunset


def get_future_data(cities: list[dict], new_date: str, header: str):
    city_data = []
    for city in cities:
        lat = city.get("latitude")
        long = city.get("longitude")
        sunrise, sunset = get_sunrise_and_set_times(lat, long, new_date)
        city_data.append((city.get("city_id"),
                          sunrise,
                          sunset,
                          new_date,
                          post_location_get_starchart(
                              header, lat, long, new_date),
                          post_location_get_moonphase(header, lat, long, new_date)))
    print("Extracted data from API")
    return city_data


def upload_data(conn, data: list[tuple]):
    cursor = conn.cursor()
    cursor.executemany(
        """INSERT INTO stargazing_status (city_id, sunrise, sunset, status_date, star_chart_url, moon_phase_url) 
        VALUES (%s, %s, %s, %s, %s, %s)""", data)
    conn.commit()
    cursor.close()
    print("Uploaded a single days data")


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    new_date = datetime.strftime(
        date.today() + timedelta(days=7), "%Y-%m-%d")  # in 8 days
    print(new_date)

    # data = get_future_data(cities, new_date, HEADER)
    # print(data)
    # upload_data(conn, data)
