from os import environ as ENV

from dotenv import load_dotenv
import requests


def explore_neow(start_date: str, end_date: str, key: str) -> dict:
    response = requests.get(
        f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={key}")
    return response.json()


if __name__ == "__main__":
    load_dotenv()
    API_KEY = ENV["API_NEOW_KEY"]
    print(explore_neow('2024-12-05', '2024-12-06', API_KEY)
          ['near_earth_objects'])
