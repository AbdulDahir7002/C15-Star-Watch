"""Extracts simple astronomic data from the AstronomyAPI"""
from os import environ as ENV

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


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
        json=body,
        timeout=10
    )
    return response.json()


def post_moon_phase(header: str, lat: float, long: float, date: str) -> None:
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
        json=body,
        timeout=10
    )
    return response.json()


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'
    # print(explore(HEADER, 51.54, -0.08, 21.7, "2025-02-11",
    #               "2025-02-11", "22:00:00"))
    print(cities)
