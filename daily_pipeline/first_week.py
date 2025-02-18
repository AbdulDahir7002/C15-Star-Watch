"""Extracts the first weeks forecast of astronomic data from the AstronomyAPI"""
from os import environ as ENV
from datetime import datetime, date, timedelta
import logging
import sys

import asyncio
import aiohttp
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


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


async def get_sunrise_and_set_times(session, lat: float, long: float, date_to_query: str):
    """Call from the open meteo API to get the daily sunrise and sunset times"""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=sunrise,sunset&timezone=auto&start_date={date_to_query}&end_date={date_to_query}"
    response = await session.get(url)
    data = await response.json()

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
    return rows


def get_constellations(connection):
    """Retrieves the constellations we need to extract data for"""
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM constellation""")
    rows = cursor.fetchall()
    cursor.close()
    return rows


async def post_location_get_starchart(session, header: str, lat: float, long: float, date_to_query: str):
    """returns the url of a star chart for specific coordinates"""
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

    response = await session.post(
        "https://api.astronomyapi.com/api/v2/studio/star-chart",
        headers={'Authorization': header},
        json=body,
        timeout=600
    )

    return response


async def post_location_get_moonphase(session, header: str, lat: float, long: float, date_to_query: str):
    """returns the url of a star chart for specific coordinates"""
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

    response = await session.post(
        "https://api.astronomyapi.com/api/v2/studio/moon-phase",
        headers={'Authorization': header},
        json=body,
        timeout=600
    )

    return response


async def format_tasks(city: dict, day: str, header: str, lat: float, long: float, session) -> asyncio.coroutines:
    """Returns all data, for a city on a given day"""
    sun_data = await get_sunrise_and_set_times(session, lat, long, day)
    star_chart = await post_location_get_starchart(session, header, lat, long, day)
    moon_phase = await post_location_get_moonphase(session, header, lat, long, day)

    star_json = await star_chart.json()
    moon_json = await moon_phase.json()

    return {"city_id": city.get("city_id"),
            "sunrise_and_sunset": sun_data,
            "date": day,
            "star_chart": star_json,
            "moon_phase": moon_json
            }


async def collate_data(header: str, city_list: list, dates: list) -> dict:
    """Formats into list of tuples in format 
    (city_id, sunrise, sunset, date, star_chart, moon_phase)"""
    logging.info("Assembling tasks...")
    async with aiohttp.ClientSession() as session:
        city_data = []
        for city in city_list:
            tasks = []
            for day in dates:
                lat = city.get("latitude")
                long = city.get("longitude")
                tasks.append(format_tasks(
                    city, day, header, lat, long, session))

            logging.info(f"Queued for all dates in city {city["city_id"]}")

            results = await asyncio.gather(*tasks)
            city_data.extend(results)
    return city_data


def format_for_insert(data: list[dict]) -> list[tuple]:
    """Format the data for insertion into the database"""
    data_as_tuple = []
    for row in data:
        data_as_tuple.append((row["city_id"],
                              datetime.strptime(' '.join(
                                  row["sunrise_and_sunset"]["daily"]["sunrise"][0].split('T')), "%Y-%m-%d %H:%M"),
                              datetime.strptime(' '.join(
                                  row["sunrise_and_sunset"]["daily"]["sunset"][0].split('T')), "%Y-%m-%d %H:%M"),
                              row["date"],
                              row["star_chart"]["data"]["imageUrl"],
                              row["moon_phase"]["data"]["imageUrl"]
                              ))
    return data_as_tuple


def seed_next_week(connection, data: list[tuple]):
    """Seed the next week of data"""
    cursor = connection.cursor()
    q = """INSERT INTO stargazing_status (city_id, sunrise, sunset, status_date, star_chart_url, moon_phase_url)
            VALUES (%s,%s,%s,%s,%s,%s)"""
    cursor.executemany(q, data)
    connection.commit()


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    configure_logs()

    cities = get_locations(conn)
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    useful_cities = [{"city_id": city.get("city_id"), "longitude": city.get(
        "longitude"), "latitude": city.get("latitude")} for city in cities]

    next_week = [datetime.strftime(
        date.today()+timedelta(days=n), "%Y-%m-%d") for n in range(8)]

    resultant_data = asyncio.run(
        collate_data(HEADER, useful_cities, next_week))
    logging.info("Tasks ran and results stored")

    finalised_data = format_for_insert(resultant_data)
    seed_next_week(conn, finalised_data)
    logging.info("Uploaded to database")

    conn.close()
