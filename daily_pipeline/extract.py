"""Extracts simple astronomic data from the AstronomyAPI"""
from os import environ as ENV

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, date, timedelta


def get_connection():
    connection = psycopg2.connect(host=ENV["DB_HOST"],
                                  user=ENV["DB_USERNAME"],
                                  dbname=ENV["DB_NAME"],
                                  password=ENV["DB_PASSWORD"],
                                  port=ENV["DB_PORT"],
                                  cursor_factory=RealDictCursor)
    return connection


def get_locations(conn):
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM city""")
    return cursor.fetchall()


def post_location_get_starchart(header: str, lat: float, long: float, date: str) -> None:
    """returns the url of a star chart for specific coordinates"""
    body = {
        "style": "default",
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": date
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
        json=body
    )
    return response.json()['data']['imageUrl']


def post_location_get_moonphase(header: str, lat: float, long: float, date: str) -> None:
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
            "date": date
        },
        "view": {
            "type": "portrait-simple",
            "orientation": "south-up"
        }
    }

    response = requests.post(
        "https://api.astronomyapi.com/api/v2/studio/moon-phase",
        headers={'Authorization': header},
        json=body
    )
    return response.json()['data']['imageUrl']


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    useful_cities = [{"city_id": city.get("city_id"), "longitude": city.get(
        "longitude"), "latitude": city.get("latitude")} for city in cities]

    next_week = [datetime.strftime(
        date.today()+timedelta(days=n), "%Y-%m-%d") for n in range(8)]

    # print(useful_cities)
    resultant_data = []
    for city in useful_cities:
        for day in next_week:
            resultant_data.append((city.get("city_id"), day, post_location_get_starchart(HEADER, city.get(
                "latitude"), city.get("longitude"), day), post_location_get_moonphase(HEADER, city.get(
                    "latitude"), city.get("longitude"), day)))

            print(f"done for {day}")
        print(f"done for {city}")
        print(resultant_data)
