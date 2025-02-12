"""Script to extract astronomy picture of the day url from the NASA API."""

import re
from os import environ
from dotenv import load_dotenv
import requests


def get_picture_of_day() -> str:
    """Returns NASA astronomy picture of the day."""
    url = f"https://api.nasa.gov/planetary/apod?api_key={environ["NASA_API_KEY"]}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        apod_data = {
            "media_type": data["media_type"],
            "title": data["title"],
            "url": data["url"]
        }
        return apod_data
    return {"error": "No astronomy picture of the day found.", "status_code": response.status_code}


def check_media_type(media_type: str) -> bool:
    """Returns a bool if media type matches video or image."""
    if isinstance(media_type, str) and media_type.lower() in ["image", "video"]:
        return True
    return False


def check_title(title: str) -> bool:
    """Returns a bool if title of correct format."""
    if isinstance(title, str):
        return True
    return False


def check_url(url: str) -> bool:
    """Returns a bool if url of correct format."""
    if isinstance(url, str):
        return bool(re.search("(https://).*", url))
    return False


def check_valid_apod(apod: dict) -> bool:
    """Return a bool for valid apod data."""
    checks = [check_media_type(apod["media_type"]), check_title(
        apod["title"]), check_url(apod["url"])]
    return all(checks)


if __name__ == "__main__":
    load_dotenv()

    apod_data = get_picture_of_day()
    if check_valid_apod(apod_data):
        print(apod_data)
    print("Invalid data.")
