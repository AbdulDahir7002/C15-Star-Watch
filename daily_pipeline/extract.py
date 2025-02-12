"""Extracts simple astronomic data from the AstronomyAPI"""
from os import environ as ENV
from datetime import datetime, date, timedelta

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


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
    cursor.close()
    connection.close()
    return cursor.fetchall()


def post_location_get_starchart(header: str, lat: float, long: float, date_to_query: str) -> None:
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


def post_location_get_moonphase(header: str, lat: float, long: float, date_to_query: str) -> None:
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
            resultant_data.append((city.get("city_id"),
                                   day,
                                   post_location_get_starchart(HEADER, city.get(
                                       "latitude"), city.get("longitude"), day),
                                   post_location_get_moonphase(HEADER, city.get(
                                       "latitude"), city.get("longitude"), day)))

            print(f"done for {day}")
        print(f"done for {city}")
        print(resultant_data)
