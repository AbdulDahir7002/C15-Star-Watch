"""Extracts simple astronomic data from the AstronomyAPI"""
import base64
import requests
from os import environ
from dotenv import load_dotenv


def get_body_locations(header: str) -> None:
    """returns the locations of celestial bodies"""
    response = requests.get("""https://api.astronomyapi.com/
                            api/v2/bodies/positions?latitude=51.54&longitude=-0.08&
                            elevation=24.7&from_date=2025-02-10&to_date=2025-02-10&time=10:31:00""",
                            headers={'Authorization': header}, timeout=10)
    print(response.json())


def get_star_chart_url(header: str, lat: float, long: float) -> None:
    """returns the url of a star chart for specific coordinates"""
    body = {
        "style": "default",
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": "2019-12-20"
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
    print(response.json())


if __name__ == "__main__":
    load_dotenv()
    auth_string = environ["BASIC_AUTH_KEY"]
    print(auth_string)
    HEADER = f'Basic {auth_string}'
    get_body_locations(HEADER)
    get_star_chart_url(HEADER, 33.775867,  -84.39733)
