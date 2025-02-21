"""Script to extract, transform and load weather data and aurora updates"""
from dotenv import load_dotenv
import logging
import sys

from aurora_status import get_connection, get_country_dict, get_current_aurora_data, get_status_per_country, insert_values_to_db

from weather_extract import get_openmeteo, get_locations, get_dates, handle_locations, clear_weather_table, insert_into_db


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


def lambda_handler(event, context):
    load_dotenv()
    conn = get_connection()

    # Aurora data
    status_dict = get_current_aurora_data()
    logging.info("Aurora data retrieved")

    country_list = get_country_dict(conn)
    country_status_list = get_status_per_country(status_dict, country_list)
    logging.info("Aurora status linked to country")

    insert_values_to_db(conn, country_status_list)
    logging.info("Aurora status data uploaded to database")

    # Weather data
    open_meteo = get_openmeteo()
    logging.info("Weather data retrieved")
    locations = get_locations(conn)
    today_str, week_str = get_dates()
    data = handle_locations(locations, open_meteo, today_str, week_str)
    logging.info("Weather status linked to location")
    clear_weather_table(conn)
    insert_into_db(data, conn)
    logging.info("Weather data uploaded to database")

    conn.close()
    return {"statusCode": 200}


if __name__ == "__main__":
    configure_logs()
    lambda_handler(None, None)
