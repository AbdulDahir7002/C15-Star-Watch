"""Module to generate data for the database."""
from datetime import datetime
import re

import requests
from bs4 import BeautifulSoup

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


def get_correct_location(results: list) -> tuple:
    """Returns the first city from the results in the UK, none otherwise."""
    for result in results:
        if result.get('country') == "United Kingdom":
            return (result['name'],
                    result['latitude'],
                    result['longitude'],
                    result['elevation'])
    return None


def get_locations():
    """Returns list of tuples with location information."""
    locations_list = []

    for city in CITIES:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5&format=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json()['results']
            locations_list.append(get_correct_location(results))

    return locations_list


def get_date_objects(startdate: str, enddate: str) -> tuple:
    """Returns date objects for date strings."""
    date_string = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", startdate)
    start_object = datetime.strptime(date_string, "%B %d %Y")
    date_string = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", enddate)
    end_object = datetime.strptime(date_string, "%B %d, %Y")
    return start_object, end_object


def get_meteor_showers():
    """Returns list of tuples of meteor shower information."""
    url = "https://www.imo.net/resources/calendar/"
    response = requests.get(url, timeout=5)
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    showers_list = []
    showers = soup.find_all(class_='shower media')

    for shower in showers:
        media_body = shower.find("div", class_="media-body")
        header = media_body.find('h3')
        timings = media_body.find('span').get_text(strip=True)

        if timings.endswith(str(datetime.today().year)):
            dates = timings.split()
            startdate = f"{dates[2]} {dates[3]} {dates[-1]}"
            enddate = f"{dates[5]} {dates[6]} {dates[-1]}"
            start_object, end_object = get_date_objects(startdate, enddate)

            showers_list.append((header.get_text(strip=True), start_object.strftime(
                "%Y-%m-%d"), end_object.strftime("%Y-%m-%d")))

    return showers_list


if __name__ == "__main__":
    locations_tuple = get_locations()
    showers_tuple = get_meteor_showers()
    print(locations_tuple)
    print(showers_tuple)
