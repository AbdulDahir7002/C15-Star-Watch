"""Extracts simple astronomic data from the AstronomyAPI"""
from os import environ
import requests

from dotenv import load_dotenv


def get_body_locations(header: str, lat: float, long: float, elevation: float, from_date: str, to_date: str, time: str) -> None:
    """returns the locations of celestial bodies"""
    response = requests.get(f"""https://api.astronomyapi.com/
                            api/v2/bodies/positions?latitude={lat}&longitude={long}&
                            elevation={elevation}&from_date={from_date}&to_date={to_date}&time={time}""",
                            headers={'Authorization': header}, timeout=10)
    return response.json()


def post_star_chart_url(header: str, lat: float, long: float, date: str) -> None:
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
    auth_string = environ["ASTRONOMY_BASIC_AUTH_KEY"]
    HEADER = f'Basic {auth_string}'
    print(get_body_locations(HEADER, 51.54, -0.08, 21.7, "2025-02-11",
                             "2025-02-11", "22:00:00"))
    print(post_star_chart_url(HEADER, 33.775867,  -84.39733, "2020-02-11"))
    print(post_moon_phase(HEADER, 33.775867, -84.39733, "2020-02-11"))
