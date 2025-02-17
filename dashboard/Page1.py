"""Page1 of the dashboard."""
from os import environ as ENV
from datetime import date, timedelta
import logging
import sys

import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv


def configure_logs():
    """Configure the logs for the whole project to refer to"""

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        handlers=[
            logging.FileHandler("logs/pipeline.log", mode="a",
                                encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


@st.cache_resource
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


@st.cache_data
def get_cities() -> list:
    """Gets a list of cities from the database."""
    connection = get_connection()
    curs = connection.cursor()
    curs.execute("SELECT city_name FROM city;")
    cities = [city[0] for city in curs.fetchall()]
    curs.close()
    return cities


@st.cache_data
def get_country(city: str) -> int:
    """Returns the country ID for a given city."""
    connection = get_connection()
    curs = connection.cursor()
    curs.execute(f"SELECT country_id FROM city WHERE city_name = '{city}';")
    country_id = curs.fetchone()[0]
    curs.close()
    return country_id


@st.cache_data(ttl=3600)
def get_aurora_info(country_id: int) -> pd.DataFrame:
    """Returns the aurora data for given country."""
    logging.info("Fetching requested aurora data...")
    connection = get_connection()
    curs = connection.cursor()
    curs.execute(
        f"SELECT * FROM aurora_status WHERE country_id = '{country_id}';")
    aurora_data = curs.fetchall()
    logging.info("Fetched!")
    data = {
        'Recording At': [str(aurora_data[-1][1])],
        'Visible by Camera': [str(aurora_data[-1][2])],
        'Visible by Eye': [str(aurora_data[-1][3])]
    }
    curs.close()
    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def get_weather_for_day(day: date, city: str) -> pd.DataFrame:
    """Returns weather information given a city and a day."""
    logging.info("Fetching requested weather data...")
    connection = get_connection()
    curs = connection.cursor()
    query = f"""
            SELECT *
            FROM weather_status
            JOIN city ON (city.city_id = weather_status.city_id)
            WHERE city_name = '{city}'
            AND status_at >= '{day}'
            AND status_at <= '{day} 23:59';
            """
    curs.execute(query)

    weather_data = [(str(weather[5]).split(" ")[1][:2],
                     round(weather[2], 1),
                     str(weather[3]).split('.')[0],
                     str(weather[4]).split('.')[0])
                    for weather in curs.fetchall()]

    data = pd.DataFrame(weather_data)
    logging.info("Fetched!")
    data.columns = ['Time', 'Temperature', 'Coverage', 'Visibility']
    data = data[data['Time'].isin(['00', '06', '12', '18', '23'])]
    data = data.T
    data.index = ['Time', 'Temperature', 'Coverage', 'Visibility']
    curs.close()
    return data


@st.cache_data(ttl=86400)
def get_stargazing_status_for_day(day: date, city: str) -> list:
    """Returns stargazing information given a city and a day."""
    logging.info("Fetching requested star chart...")
    connection = get_connection()
    curs = connection.cursor()
    query = f"""
            SELECT stargazing_status.*, city_name
            FROM stargazing_status JOIN city
            ON (city.city_id = stargazing_status.city_id)
            WHERE city_name = '{city}'
            AND status_date = '{day}';
            """
    curs.execute(query)
    stargazing_status = curs.fetchone()
    logging.info("Fetched!")
    curs.close()
    return stargazing_status


def get_meteor_showers_for_day(day) -> pd.DataFrame:
    """Gets meteor showers occurring during given day."""
    logging.info("Fetching requested meteor shower data...")
    connection = get_connection()
    curs = connection.cursor()
    query = f"""
            SELECT *
            FROM meteor_shower
            WHERE '{day}' >= shower_start
            AND '{day}' <= shower_end;
            """
    curs.execute(query)
    results = curs.fetchall()
    curs.close()
    df = pd.DataFrame(results)
    logging.info("Fetched!")
    if len(results) > 0:
        df.columns = ["id", "Name", "Start Date", "End Date", "Peak Date"]
        return df

    return None


def get_emoji_for_weather(weather: pd.DataFrame) -> str:
    """Uses the weather DF to return an appropriate emoji."""
    weather = weather.T
    weather['Coverage'] = pd.to_numeric(weather['Coverage'])
    average = weather['Coverage'].mean()

    if average >= 85:
        return '&#x2601;'
    if average >= 65:
        return '&#x26C5;'
    if average >= 30:
        return '&#x1F324;'
    return '&#9728;'


def get_days() -> list:
    """Returns a list of dates from today to a week from now."""
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]
    days.append("Week")
    return days


def column_one(weather: pd.DataFrame, star_status: list) -> None:
    """Writes info intended for left column."""
    if weather is None:
        st.write("No weather for this date/location.")
    else:
        emoji = get_emoji_for_weather(weather)
        st.markdown(f'<p>Weather Forecast {emoji}</p>',
                    unsafe_allow_html=True)
        st.markdown(weather.to_html(header=False), unsafe_allow_html=True)

    st.write("Moonphase")
    if star_status is None:
        st.write("No data for this date/location.")
    else:
        st.image(star_status[6])


def column_two(showers, star_status: list):
    """Writes info intended for right column."""
    st.markdown(f"<p>Sunset / Sunrise &#9728;</p>",
                unsafe_allow_html=True)
    if star_status is None:
        st.write("No data for this date/location.")
    else:
        st.write("Sunrise: ", date.strftime(star_status[2], '%H:%M'), 'AM')
        st.write("Sunset: ", date.strftime(star_status[3], '%H:%M'), 'PM')

    st.write("Meteor showers")

    if showers is None:
        st.write("No meteor showers on this day.")
    else:
        st.markdown(showers.to_html(index=False), unsafe_allow_html=True)


def app():
    """The function ran when the user switches to this page."""
    load_dotenv()
    configure_logs()

    city = st.sidebar.selectbox('City', get_cities())
    country_id = get_country(city)
    day = st.sidebar.selectbox('Day', get_days())
    showers = get_meteor_showers_for_day(day)
    aurora = get_aurora_info(country_id)
    weather = get_weather_for_day(day, city)
    star_status = get_stargazing_status_for_day(day, city)

    st.title(city)
    col1, col2 = st.columns(2)
    with col1:
        column_one(weather, star_status)
    with col2:
        column_two(showers, star_status)

    st.write("Starchart")
    if star_status is None:
        st.write("No Data for this date/location.")
        logging.debug("No data found in star status")
    else:
        st.image(star_status[5])

    if day == date.today():
        st.write("Aurora Activity")
        st.markdown(aurora.to_html(index=False), unsafe_allow_html=True)


if __name__ == "__main__":
    app()
