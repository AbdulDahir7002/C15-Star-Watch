"""Extracts simple astronomic data from the AstronomyAPI"""
import base64
import requests
from os import environ
from dotenv import load_dotenv


def get_body_locations(header: str, lat: float, long: float) -> None:
    """returns the locations of celestial bodies"""
    response = requests.get(f"https://api.astronomyapi.com/api/v2/bodies/positions?latitude={lat}&longitude={long}&elevation=24.7&from_date=2025-02-10&to_date=2025-02-10&time=10:31:00""",
                            headers={'Authorization': header}, timeout=10)
    return response.json()


def get_star_chart_url(header: str, lat: float, long: float) -> None:
    """returns the url of a star chart for specific coordinates"""
    body = {
        "style": "default",
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": "2025-10-20"
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
        json=body
    )
    return response.json()


def get_moon_phase(header: str, lat: float, long: float) -> None:
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
            "date": "2020-11-01"
        },
        "view": {
            "type": "portrait-simple",
            "orientation": "south-up"
        }
    }

    response = requests.post(
        "https://api.astronomyapi.com/api/v2/studio/moon-phase",
        headers={'Authorization': header},
        json=body
    )
    return response.json()


if __name__ == "__main__":
    load_dotenv()
    auth_string = environ["ASTRONOMY_BASIC_AUTH_KEY"]
    print(auth_string)
    HEADER = f'Basic {auth_string}'
    get_body_locations(HEADER, 51.54, -0.08)
    print(get_star_chart_url(HEADER, 33.775867,  -84.39733))
    print(get_moon_phase(HEADER, 33.775867, -84.39733))
