"""Module to generate data for the database."""
from datetime import datetime
import re
from os import environ as ENV
import importlib
import logging

import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from logs_setup.logs import configure_logs


CITIES = [
    "Aberdeen", "Armagh", "Bangor", "Bath", "Belfast", "Birmingham", "Bradford",
    "Brighton & Hove", "Bristol", "Cambridge", "Canterbury", "Cardiff", "Carlisle",
    "Chelmsford", "Chester", "Chichester", "Colchester", "Coventry", "Derby",
    "Doncaster", "Dundee", "Dunfermline", "Durham", "Edinburgh", "Ely", "Exeter",
    "Glasgow", "Gloucester", "Hereford", "Inverness", "Kingston upon Hull",
    "Lancaster", "Leeds", "Leicester", "Lichfield", "Lincoln", "Lisburn",
    "Liverpool", "London", "Londonderry", "Manchester", "Milton Keynes",
    "Newcastle upon Tyne", "Newport", "Newry", "Norwich", "Nottingham", "Oxford",
    "Perth", "Peterborough", "Plymouth", "Portsmouth", "Preston", "Ripon",
    "Salford", "Salisbury", "Sheffield", "Southampton", "Southend-on-Sea",
    "St Albans", "St Asaph", "St David's", "Stirling", "Stoke-on-Trent",
    "Sunderland", "Swansea", "Truro", "Wakefield", "Wells", "Westminster",
    "Winchester", "Wolverhampton", "Worcester", "Wrexham", "York"
]


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


def get_correct_location(results: list) -> tuple:
    """Returns the first city from the results in the UK, none otherwise."""
    countries = {"England": 1,
                 "Scotland": 2,
                 "Wales": 3,
                 "Northern Ireland": 4
                 }

    for result in results:
        if result.get('country') == "United Kingdom":
            if result['name'] == 'Londonderry':
                result['country'] = "Northern Ireland"
            else:
                result['country'] = result['admin1']
            return (result['name'],
                    countries.get(result['country']),
                    result['latitude'],
                    result['longitude'],
                    result['elevation']
                    )
    return None


def get_locations(CITIES: list[str]):
    """Returns list of tuples with location information."""
    locations_list = []

    for city in CITIES:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json()['results']
            location = get_correct_location(results)
            if location:
                locations_list.append(location)

    return locations_list


def get_date_objects(startdate: str, enddate: str) -> tuple:
    """Returns date objects for date strings."""
    date_string = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", startdate)
    start_object = datetime.strptime(date_string, "%B %d %Y")
    date_string = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", enddate)
    end_object = datetime.strptime(date_string, "%B %d, %Y")
    return start_object, end_object


def convert_peak_night_to_datetime(peak_night: str) -> datetime:
    """Converts the peak_night string from Nov16-17 to 2025-11-16."""
    peak_night = peak_night.split(",")[0].split("-")[0]
    months = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }
    year = datetime.today().year
    return datetime(year, months.get(peak_night[:3]), int(peak_night[3:]))


def get_meteor_showers():
    """Returns list of tuples of meteor shower information."""
    logging.info("Calling for meteor data...")
    url = "https://www.imo.net/resources/calendar/"
    response = requests.get(url, timeout=5)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    showers_list = []
    showers_divs = soup.find_all(class_='shower media')

    for shower in showers_divs:
        media_body = shower.find("div", class_="media-body")
        left_body = shower.find("div", class_="media-left")

        peak = left_body.find("strong").get_text(strip=True)
        peak_night = convert_peak_night_to_datetime(peak)

        header = media_body.find('h3')
        timings = media_body.find('span').get_text(strip=True)

        if timings.endswith(str(datetime.today().year)):
            dates = timings.split()
            startdate = f"{dates[2]} {dates[3]} {dates[-1]}"
            enddate = f"{dates[5]} {dates[6]} {dates[-1]}"
            start_object, end_object = get_date_objects(startdate, enddate)

            showers_list.append((header.get_text(strip=True), start_object.strftime(
                "%Y-%m-%d"), end_object.strftime("%Y-%m-%d"), peak_night))

    return showers_list


def insert_countries(connection) -> None:
    """Inserts countries England, Scotland, Wales and Northern Ireland into the database."""
    curs = connection.cursor()
    query = """
            INSERT INTO country (country_id, country_name)
            VALUES (1, 'England'), (2, 'Scotland'), (3, 'Wales'), (4, 'Northern Ireland');
            """
    curs.execute(query)
    connection.commit()
    curs.close()


def insert_cities(locations_list, connection) -> None:
    """Inserts cities into the database."""
    curs = connection.cursor()
    query = """
            INSERT INTO city (city_name, country_id, latitude, longitude, elevation)
            VALUES %s
            """
    execute_values(curs, query, locations_list)
    connection.commit()
    curs.close()


def insert_meteor_showers(showers_list, connection) -> None:
    """Inserts meteor showers in the database."""
    curs = connection.cursor()
    query = """
            INSERT INTO meteor_shower (meteor_shower_name, shower_start, shower_end, shower_peak)
            VALUES %s
            """
    execute_values(curs, query, showers_list)
    connection.commit()
    curs.close()


def clear_tables(connection):
    """Empties city, country and meteor shower."""
    curs = connection.cursor()
    query = """
            DELETE FROM city;
            DELETE FROM country;
            DELETE FROM meteor_shower;
            """
    curs.execute(query)
    connection.commit()
    curs.close()


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    configure_logs()

    locations = get_locations(CITIES)
    showers = get_meteor_showers()
    logging.info("Meteor data retrieved")

    clear_tables(conn)
    logging.warning("Tables city, country, meteor_shower CLEARED")

    insert_countries(conn)
    logging.info("Country data uploaded")

    insert_cities(locations, conn)
    logging.info("City data uploaded")

    insert_meteor_showers(showers, conn)
    logging.info("Meteor data uploaded")

    logging.info("Finished")
    conn.close()
