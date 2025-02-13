from os import environ as ENV
from datetime import date, timedelta

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


def get_country(city: str, connection) -> int:
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


def get_weather_for_day(day, city, connection):
    """Returns weather information given a city and a day."""
    curs = connection.cursor()
    curs.execute(
        f"SELECT * FROM weather_status JOIN city ON (city.city_id = weather_status.city_id) WHERE city_name = '{city}' AND status_at >= '{day}'  AND status_at <= '{day} 23:59';")
    weather_data = [(str(weather[5]).split(" ")[1][:2], weather[2], weather[3], weather[4])
                    for weather in curs.fetchall()]
    data = pd.DataFrame(weather_data)
    data.columns = ['Time', 'Temperature', 'Coverage', 'Visibility']
    curs.close()
    return data[data['Time'].isin(['00', '06', '12', '18', '23'])]


def get_days() -> list:
    """Returns a list of dates from today to a week from now."""
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]
    days.append("Week")
    return days


def column_one() -> None:
    """Writes info intended for left column."""
    st.write("Weather Forecast")


def column_two():
    """Writes info intended for right column."""
    st.write("Sunset / Sunrise")
    st.write("Sunset/rise goes here.")


def app():
    load_dotenv()
    connection = get_connection()

    city = st.sidebar.selectbox('City', get_cities(connection))
    country_id = get_country(city, connection)
    day = st.sidebar.selectbox('Day', get_days())

    aurora = get_aurora_info(country_id, connection)

    st.title(city)

    col1, col2 = st.columns(2)
    with col1:
        column_one()
        st.write(get_weather_for_day(day, city, connection))
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
