"""Streamlit dashboard home page."""
from os import environ as ENV
import requests

from datetime import date
from dotenv import load_dotenv
import streamlit as st

from Page1 import get_constellations, get_constellation_code, get_lat_and_long, post_location_get_starchart, create_scroll_image, get_connection


@st.cache_data
def get_nasa_apod() -> dict:
    """Returns the data for the NASA APOD."""
    API_KEY = ENV['NASA_APOD_KEY']
    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    print(data)
    return data


def display_apod(apod: dict) -> None:
    """Displays APOD on streamlit page."""
    st.markdown("<h3>NASA Picture of the Day</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.image(apod['url'])
    with col2:
        st.write(apod['title'], '-', apod['date'])
        st.write(apod['explanation'])


def get_constellation_url(constellation: str) -> str:
    """Fetches url for corresponding constellation from the database."""
    connection = get_connection()
    query = f"""SELECT constellation_url
                FROM constellation
                WHERE constellation_name = '{constellation}';"""
    with connection.cursor() as curs:
        curs.execute(query)
        result = curs.fetchone()
    return result[0]


def display_constellation() -> None:
    """Displays the constellation starchart section."""
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'
    st.markdown("<h3>Constellation Starchart</h3>", unsafe_allow_html=True)
    st.markdown("""Here, you can select any constellation you are curious about. 
                    Keep in mind, this is the chart from London's perspective.""")
    constellation = st.selectbox('Select constellation:', get_constellations())
    create_scroll_image(get_constellation_url(constellation), 617)


def app():
    """Function that is ran when the user selects the home page."""
    load_dotenv()

    st.title("Starwatch")
    st.markdown("### Welcome to Starwatch!")
    st.markdown("""We are dedicated to bringing you the information you need to know
                to have a _**great night stargazing**_! We hope you enjoy, make sure to let us know if you were like to see more. 
                There is also a subscribe page that you can use to automatically get a summary for the week. 
                Please feel free to look at the interest sections on this page.""")
    st.write("Select a page from the sidebar to explore forecasts and trends, or stay here for more general information.")

    with st.container(border=True):
        display_apod(get_nasa_apod())

    with st.container(border=True):
        display_constellation()


if __name__ == "__main__":
    app()
