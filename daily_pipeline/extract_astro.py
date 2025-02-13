"""Extracts simple astronomic data from the AstronomyAPI"""
from os import environ as ENV
from datetime import datetime, date, timedelta

import asyncio
import aiohttp
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


async def get_sunrise_and_set_times(session, lat: float, long: float, date: str):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=sunrise,sunset&timezone=auto&start_date={date}&end_date={date}"
    response = await session.get(url)
    data = response
    # sunrise = data['daily']['sunrise'][0]
    # sunset = data['daily']['sunset'][0]

    return data

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
    connection.close()
    return rows


async def post_location_get_starchart(session, header: str, lat: float, long: float, date_to_query: str) -> None:
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

    response = await session.post(
        "https://api.astronomyapi.com/api/v2/studio/star-chart",
        headers={'Authorization': header},
        json=body,
        timeout=60
    )

    return response


async def post_location_get_moonphase(session, header: str, lat: float, long: float, date_to_query: str) -> None:
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

    response = await session.post(
        "https://api.astronomyapi.com/api/v2/studio/moon-phase",
        headers={'Authorization': header},
        json=body,
        timeout=60
    )
    return response
# response.json()['data']['imageUrl']


async def format_data(city: dict, day: str, header: str, lat: float, long: float, session) -> asyncio.coroutines:
    """Returns all data, for a city on a given day"""
    sun_data = await get_sunrise_and_set_times(session, lat, long, day)
    star_chart = await post_location_get_starchart(session, header, lat, long, day)
    moon_phase = await post_location_get_moonphase(session, header, lat, long, day)

    return {"city_id": city.get("city_id"),
            "sunrise_and_sunset": sun_data,
            "date": day,
            "star_chart": star_chart,
            "moon_phase": moon_phase
            }


async def collate_data(header, cities, dates):
    """Formats into list of tuples in format 
    (city_id, sunrise, sunset, date, star_chart, moon_phase)"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for city in cities:
            for day in dates:
                lat = city.get("latitude")
                long = city.get("longitude")
                tasks.append(format_data(
                    city, day, header, lat, long, session))
                print(f"Queued for {day}")
            print(f"Queued for {city}")

        resultant_data = await asyncio.gather(*tasks)

    return resultant_data


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    useful_cities = [{"city_id": city.get("city_id"), "longitude": city.get(
        "longitude"), "latitude": city.get("latitude")} for city in cities]

    next_week = [datetime.strftime(
        date.today()+timedelta(days=n), "%Y-%m-%d") for n in range(8)]

    resultant_data = asyncio.run(
        collate_data(HEADER, useful_cities, next_week))

    for part in resultant_data:
        print(part.get("star_chart").json()['data']['image_url'])
