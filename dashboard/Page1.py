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
    """Returns the country ID for a given city."""
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


def get_weather_for_day(day: date, city: str, connection) -> pd.DataFrame:
    """Returns weather information given a city and a day."""
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
    data.columns = ['Time', 'Temperature', 'Coverage', 'Visibility']
    data = data[data['Time'].isin(['00', '06', '12', '18', '23'])]
    data = data.T
    data.index = ['Time', 'Temperature', 'Coverage', 'Visibility']
    curs.close()
    return data


def get_stargazing_status_for_day(day: date, city: str, connection) -> list:
    """Returns stargazing information given a city and a day."""
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
    curs.close()
    return stargazing_status


def get_meteor_showers_for_day(stargazing_id: int, connection) -> pd.DataFrame:
    """Gets meteor showers linked to given stargazing status"""
    curs = connection.cursor()
    query = f"""
            SELECT *
            FROM meteor_shower_assignment
            JOIN meteor_shower
            ON (meteor_shower.meteor_shower_id = meteor_shower_assignment.meteor_shower_id)
            WHERE stargazing_status_id = {stargazing_id};
            """
    ...


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
    if average < 30:
        return '&#57418;'


def get_days() -> list:
    """Returns a list of dates from today to a week from now."""
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]
    days.append("Week")
    return days


def column_one(weather: pd.DataFrame, star_status: list) -> None:
    """Writes info intended for left column."""
    st.write("Weather Forecast")
    emoji = get_emoji_for_weather(weather)
    st.markdown(f'<p>Weather Forecast {emoji}</p>',
                unsafe_allow_html=True)
    st.markdown(weather.to_html(header=False), unsafe_allow_html=True)
    st.write("Moonphase")
    st.image(star_status[6])


def column_two(star_status: list):
    """Writes info intended for right column."""
    st.write("Sunset / Sunrise")
    st.write("Sunrise: ", date.strftime(star_status[2], '%H:%M'), 'AM')
    st.write("Sunset: ", date.strftime(star_status[3], '%H:%M'), 'PM')
    st.write("Meteor showers")


def app():
    load_dotenv()
    connection = get_connection()

    city = st.sidebar.selectbox('City', get_cities(connection))
    country_id = get_country(city, connection)
    day = st.sidebar.selectbox('Day', get_days())

    aurora = get_aurora_info(country_id, connection)
    weather = get_weather_for_day(day, city, connection)
    star_status = get_stargazing_status_for_day(day, city, connection)

    st.title(city)
    col1, col2 = st.columns(2)
    with col1:
        column_one(weather, star_status)
    with col2:
        column_two(star_status)

    st.write("Starchart")
    st.image(star_status[5])

    if day == date.today():
        st.write("Aurora Activity")
        st.markdown(aurora.to_html(index=False), unsafe_allow_html=True)

    connection.close()


if __name__ == "__main__":
    app()
