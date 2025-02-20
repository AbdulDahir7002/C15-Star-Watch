"""Runs the pipeline for 7 days from current date, to keep up with forecast"""
from os import environ as ENV
from datetime import datetime, date, timedelta
import sys
import logging

import asyncio
import aiohttp
import requests
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values


def configure_logs():
    """Configure the logs for the whole project to refer to"""

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        handlers=[
            logging.FileHandler("log_files/pipeline.log", mode="a",
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


def get_constellation_codes(connection):
    """Fetches constellation codes from the database"""
    cursor = connection.cursor()
    q = """SELECT constellation_code FROM constellation"""
    cursor.execute(q)
    codes = cursor
    cursor.close()
    return codes


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


def upload_daily_data(conn, data: list[tuple]):
    """Upload the next day's data"""
    cursor = conn.cursor()
    cursor.execute_values(
        """INSERT INTO stargazing_status (city_id, sunrise, sunset, status_date, star_chart_url, moon_phase_url) 
        VALUES (%s, %s, %s, %s, %s, %s)""", data)
    conn.commit()
    cursor.close()


async def get_daily_contellation(header, lat, long, date_to_query, constellation_code, session):
    """Returns the given constellation from London's perspective"""
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
                "constellation": constellation_code
            }
        }
    }
    print(body)
    try:
        await asyncio.sleep(2)
        response = await session.post(
            "https://api.astronomyapi.com/api/v2/studio/star-chart",
            headers={'Authorization': header},
            json=body,
            timeout=None
        )
        result = await response.json()
        return {"code": constellation_code, "url": result}

    except KeyError:
        print(response.json())
        print(body)


async def gather_tasks(code_list, header, lat, long, date_to_query):
    """Have the tasks run in async fashion"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for code in code_list:
            tasks.append(get_daily_contellation(
                header, lat, long, date_to_query, code["constellation_code"], session))
        results = await asyncio.gather(*tasks)
        return results


def format_for_db_update(data):
    """Makes the results of the tasks digestible for the database"""
    formatted_data = []
    for row in data:
        print(row)
        row["new_url"] = row["url"]["data"]["imageUrl"]
        formatted_data.append(row)
    return formatted_data


def upload_constellation_urls(conn, data: list[dict]):
    """Upload constellation urls"""
    cursor = conn.cursor()
    q = """UPDATE constellation SET constellation_url = %s WHERE constellation_code = %s"""

    for row in data:
        cursor.execute(q, [row["new_url"], row["code"]])
    conn.commit()
    cursor.close()


def check_run_errors(batch, section, header, lat, long, current_date):
    """Checks for errors"""
    while any(["data" not in row.get("url") for row in batch]):
        print("Error in the batch!")
        print(batch)
        batch = asyncio.run(gather_tasks(
            section, header, lat, long, current_date))
    return batch


def handler(event, context):
    """Lambda function handler"""
    load_dotenv()
    configure_logs()

    LONDON_LONG = 51.5072
    LONDON_LAT = 0.1276
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    conn = get_connection()
    cities = get_locations(conn)
    const_codes = get_constellation_codes(conn)

    current_date = datetime.strftime(
        date.today() + timedelta(days=7), "%Y-%m-%d")

    forecast_data = get_future_data(cities, current_date, HEADER)
    logging.info("Star chart and Moon phase url's retrieved")

    daily_const = []

    first_batch = asyncio.run(gather_tasks(
        const_codes[:11], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    first_batch = check_run_errors(first_batch, const_codes[:11], HEADER,
                                   LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(first_batch)

    second_batch = asyncio.run(gather_tasks(
        const_codes[11:22], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    second_batch = check_run_errors(second_batch, const_codes[11:22], HEADER,
                                    LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(second_batch)

    third_batch = asyncio.run(gather_tasks(
        const_codes[22:33], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    third_batch = check_run_errors(
        third_batch, const_codes[22:33], HEADER, LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(third_batch)

    fourth_batch = asyncio.run(gather_tasks(
        const_codes[33:44], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    fourth_batch = check_run_errors(
        fourth_batch, const_codes[33:44], HEADER, LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(fourth_batch)

    fifth_batch = asyncio.run(gather_tasks(
        const_codes[44:55], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    fifth_batch = check_run_errors(
        fifth_batch, const_codes[44:55], HEADER, LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(fifth_batch)

    sixth_batch = asyncio.run(gather_tasks(
        const_codes[55:66], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    sixth_batch = check_run_errors(
        sixth_batch, const_codes[55:66], HEADER, LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(sixth_batch)

    seventh_batch = asyncio.run(gather_tasks(
        const_codes[66:77], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    seventh_batch = check_run_errors(
        seventh_batch, const_codes[66:77], HEADER, LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(seventh_batch)

    eighth_batch = asyncio.run(gather_tasks(
        const_codes[77:], HEADER, LONDON_LAT, LONDON_LONG, current_date))

    eighth_batch = check_run_errors(
        eighth_batch, const_codes[77:], HEADER, LONDON_LAT, LONDON_LONG, current_date)

    daily_const.extend(eighth_batch)

    formatted_const = format_for_db_update(daily_const)
    logging.info("Todays constellation url's retrieved")

    upload_constellation_urls(conn, formatted_const)
    logging.info("Uploaded todays constellations")

    upload_daily_data(conn, forecast_data)
    logging.info("Uploaded a single days data - star chart and moon phase")
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

    # upload_data(conn, data)
    logging.info("Uploaded a single days data")
    conn.close()
