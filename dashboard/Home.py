"""Streamlit dashboard home page."""
from os import environ as ENV

from datetime import date
from dotenv import load_dotenv
import streamlit as st

from Page1 import get_constellations, get_constellation_code, get_lat_and_long, post_location_get_starchart


def app():
    """Function that is ran when the user selects the home page."""
    load_dotenv()
    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'
    st.title("Starwatch")
    st.write("Welcome to starwatch!")
    st.write("Select a page from the sidebar to explore more.")
    constellation = st.selectbox('Constellation', get_constellations())
    code = get_constellation_code(constellation)
    city = 'Aberdeen'
    lat, long = get_lat_and_long(city)
    day = date.today()
    url = post_location_get_starchart(
        HEADER, lat, long, day, code)
    st.image(url)


if __name__ == "__main__":
    app()
