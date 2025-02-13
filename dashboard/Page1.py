from os import environ as ENV

import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv


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


def get_cities(connection) -> list:
    """Gets a list of cities from the database."""
    curs = connection.cursor()
    curs.execute("SELECT city_name FROM city;")
    cities = [city[0] for city in curs.fetchall()]
    curs.close()
    return cities


def get_country(city, connection) -> int:
    """Returns the country ID for a given city"""
    curs = connection.cursor()
    curs.execute(f"SELECT country_id FROM city WHERE city_name = '{city}';")
    country_id = curs.fetchone()[0]
    curs.close()
    return country_id


def get_aurora_info(country_id: int, connection) -> pd.DataFrame:
    """Returns the aurora data for given country."""
    curs = connection.cursor()
    curs.execute(
        f"SELECT * FROM aurora_status WHERE country_id = '{country_id}';")
    aurora_data = curs.fetchall()
    data = {
        'Recording At': [str(aurora_data[-1][1])],
        'Visible by Camera': [str(aurora_data[-1][2])],
        'Visible by Eye': [str(aurora_data[-1][3])]
    }
    curs.close()
    return pd.DataFrame(data)


def column_one():
    st.write("Weather Forecast")
    st.write("Weather forecast goes here.")


def column_two():
    st.write("Sunset / Sunrise")
    st.write("Sunset/rise goes here.")


def app():
    load_dotenv()
    connection = get_connection()

    city = st.sidebar.selectbox('City', get_cities(connection))
    country_id = get_country(city, connection)
    aurora = get_aurora_info(country_id, connection)

    st.title(city)

    col1, col2 = st.columns(2)
    with col1:
        column_one()
    with col2:
        column_two()

    st.write("Moonphase")
    st.image("https://cdn.mos.cms.futurecdn.net/xXp45gLeBTBt4jPuZcawUJ-1200-80.jpg",
             use_container_width=True)

    st.write("Aurora activity")
    st.markdown(aurora.to_html(index=False), unsafe_allow_html=True)

    st.write("Meteor showers")

    st.write("Starchart")

    connection.close()


if __name__ == "__main__":
    app()
