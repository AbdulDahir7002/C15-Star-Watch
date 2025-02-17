"""Extracts, transforms and loads the occurences of aurora events from a to an RDS"""
from xml.etree import ElementTree as ET
from os import environ as ENV
import requests
import logging

import psycopg2
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

# DB connect


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


def query_db(conn, query: str, params: tuple) -> list[tuple]:
    """Query the database and return a list of tuples of values"""
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        output = cursor.fetchall()
    return output


def insert_db(conn, query: str, params: tuple) -> tuple:
    with conn.cursor() as cursor:
        cursor.execute(query, params)
    conn.commit()

# Extract


def get_country_dict(conn):
    """Returns a dict of country names assigned to IDs"""
    query = "SELECT * from country;"
    countries = query_db(conn, query, ())
    country_dict = {}

    for country in countries:
        country_dict[country[1]] = country[0]

    return country_dict


def get_current_aurora_data() -> dict:
    """Fetch current aurora status and last update"""
    logging.info("Retrieving Aurora data...")
    response = requests.get(
        "https://aurorawatch-api.lancs.ac.uk/0.2/status/current-status.xml", timeout=10)
    root = ET.fromstring(response.text)
    last_update = root[0][0].text
    current_status = root[1].attrib["status_id"]
    return {"last_updated": last_update, "current_status": current_status}


# Transform
def get_status_per_country(status: dict, countries: dict) -> list[tuple]:
    """create a status database entry for each country"""
    # tuple order (country_id, status_at, camera_visibility, naked_eye_visibility)
    if status["current_status"] == "green":
        countries_status = [
            (countries["Scotland"], status["last_updated"], False, False),
            (countries["England"], status["last_updated"], False, False),
            (countries["Wales"], status["last_updated"], False, False),
            (countries["Northern Ireland"], status["last_updated"],
             False, False)
        ]
    elif status["current_status"] == "yellow":
        countries_status = [
            (countries["Scotland"], status["last_updated"], True, True),
            (countries["England"], status["last_updated"], True, False),
            (countries["Wales"], status["last_updated"], False, False),
            (countries["Northern Ireland"], status["last_updated"],
             True, False)
        ]
    elif status["current_status"] == "amber":
        countries_status = [
            (countries["Scotland"], status["last_updated"], True, True),
            (countries["England"], status["last_updated"], True, True),
            (countries["Wales"], status["last_updated"], True, False),
            (countries["Northern Ireland"], status["last_updated"],
             True, True)
        ]
    elif status["current_status"] == "red":
        countries_status = [
            (countries["Scotland"], status["last_updated"], True, True),
            (countries["England"], status["last_updated"], True, True),
            (countries["Wales"], status["last_updated"], True, True),
            (countries["Northern Ireland"], status["last_updated"],
             True, True)
        ]
    else:
        raise ValueError("Current status is unidentified")
    return countries_status

# Load


def insert_values_to_db(conn, country_status: list):
    """Insert the current aurora status into aurora_status table"""
    query = """
            INSERT INTO aurora_status (
                country_id, 
                aurora_status_at, 
                camera_visibility, 
                naked_eye_visibility)
            VALUES
                (%s, %s, %s, %s)
            ON CONFLICT (
                country_id,
                aurora_status_at,
                camera_visibility,
                naked_eye_visibility)
            DO NOTHING
            """
    for row in country_status:
        insert_db(conn, query, row)


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    configure_logs()

    status_dict = get_current_aurora_data()
    logging.info("Aurora data retrieved")

    country_list = get_country_dict(conn)
    print(status_dict, country_list)

    country_status_list = get_status_per_country(status_dict, country_list)
    logging.info("Aurora status linked to country")
    print(country_status_list)

    insert_values_to_db(conn, country_status_list)
    logging.info("Aurora status data uploaded to database")
    conn.close()
