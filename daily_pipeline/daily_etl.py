"""Runs the pipeline for 7 days from current date, to keep up with forecast"""
from os import environ as ENV
from datetime import datetime, date, timedelta
import sys
import logging

import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor


def configure_logs():
    """Configure the logs for the whole project to refer to"""

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        handlers=[
            logging.FileHandler("logs/pipeline.log", mode="a",
                                encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def get_connection():
    """Gets a connection to the database"""
    connection = psycopg2.connect(host=ENV["DB_HOST"],
                                  user=ENV["DB_USERNAME"],
                                  dbname=ENV["DB_NAME"],
                                  password=ENV["DB_PASSWORD"],
                                  port=ENV["DB_PORT"],
                                  cursor_factory=RealDictCursor)
    return connection


def get_locations(connection):
    """Retrieves the cities we need to extract data for"""
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM city""")
    rows = cursor.fetchall()
    cursor.close()
    return rows


def post_location_get_starchart(header: str, lat: float, long: float, date_to_query: str):
    """returns the url of a star chart for specific coordinates"""
    logging.info("Getting star chart")
    body = {
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": date_to_query
        },
        "view": {
            "type": "area",
            "parameters": {
                "position": {
                    "equatorial": {
                        "rightAscension": 0.0,
                        "declination": lat
                    }
                }
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
    logging.info("Getting moonphase")
    body = {
        "format": "png",
        "style": {
            "moonStyle": "default",
            "backgroundStyle": "stars",
            "backgroundColor": "red",
            "headingColor": "white",
            "textColor": "white"
        },
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": date_to_query
        },
        "view": {
            "type": "portrait-simple",
            "orientation": "north-up"
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
    logging.info("Getting sunrise and set times")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=sunrise,sunset&timezone=auto&start_date={date_to_query}&end_date={date_to_query}"
    response = requests.get(url)
    data = response.json()
    sunrise = data['daily']['sunrise'][0]
    sunset = data['daily']['sunset'][0]

    return sunrise, sunset


def get_future_data(cities: list[dict], new_date: str, header: str):
    """Get the data from the API with the given date"""
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
    return city_data


def upload_data(conn, data: list[tuple]):
    """Upload the next day's data"""
    cursor = conn.cursor()
    cursor.executemany(
        """INSERT INTO stargazing_status (city_id, sunrise, sunset, status_date, star_chart_url, moon_phase_url) 
        VALUES (%s, %s, %s, %s, %s, %s)""", data)
    conn.commit()
    cursor.close()


def handler(event, context):
    """Lambda function handler"""
    load_dotenv()
    configure_logs()

    conn = get_connection()
    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    new_date = datetime.strftime(
        date.today() + timedelta(days=7), "%Y-%m-%d")

    data = get_future_data(cities, new_date, HEADER)
    logging.info("Star chart and Moon phase url's retrieved")

    upload_data(conn, data)
    logging.info("Uploaded a single days data")
    conn.close()


if __name__ == "__main__":
    load_dotenv()
    configure_logs()

    conn = get_connection()
    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    new_date = datetime.strftime(
        date.today() + timedelta(days=7), "%Y-%m-%d")  # in 8 days

    data = get_future_data(cities, new_date, HEADER)
    logging.info("Star chart and Moon phase url's retrieved")

    upload_data(conn, data)
    logging.info("Uploaded a single days data")
    conn.close()
