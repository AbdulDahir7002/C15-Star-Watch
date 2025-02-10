import base64
import requests
from os import environ
from dotenv import load_dotenv


def get_body_locations(auth_code: str) -> None:
    response = requests.get("https://api.astronomyapi.com/api/v2/bodies/positions?latitude=51.54&longitude=-0.08&elevation=24.7&from_date=2025-02-10&to_date=2025-02-10&time=10:31:00",
                            headers={'Authorization': header})
    print(response.json())


def get_star_chart_url(auth_code: str) -> None:

    body = {
        "style": "default",
        "observer": {
            "latitude": 33.775867,
            "longitude": -84.39733,
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
    authString = environ["BASIC_AUTH_KEY"]
    print(authString)
    header = f'Basic {authString}'
    get_body_locations(header)
    get_star_chart_url(header)
