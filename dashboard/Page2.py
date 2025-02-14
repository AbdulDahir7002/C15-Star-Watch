"""Page 1 of the Dashboard"""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2.extras
import streamlit as st
import pandas as pd
import psycopg2
from streamlit_timeline import st_timeline

# DB connect


def get_connection():
    """Returns psycopg2 connection object."""
    connection = psycopg2.connect(
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        cursor_factory=psycopg2.extras.RealDictCursor
    )
    return connection


def query_db(conn, query: str, params: tuple) -> list[dict]:
    """Query the database and return a list of tuples of values."""
    print(conn)
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        output = cursor.fetchall()
    return output


def get_sunrise_sunset_df(conn):
    """Returns a dataframe containing sunrise and sunset data."""
    q = """
            SELECT 
                s.stargazing_status_id, 
                s.sunrise,
                s.sunset, 
                s.status_date 
            FROM stargazing_status AS s
            """
    rows = query_db(conn, q, [])
    return pd.DataFrame(rows)


def get_weather_status_week_df(conn):
    """Returns a dataframe containing weather status data."""
    q = """
        SELECT 
            w.weather_status_id, 
            c.city_name, 
            w.temperature, 
            w.coverage, 
            w.visibility,
            w.status_at
        FROM
            weather_status AS w
        JOIN
            city as c USING (city_id)
        WHERE
            w.status_at <= CURRENT_DATE + INTERVAL '2 days'; 
        """
    rows = query_db(conn, q, [])
    return pd.DataFrame(rows)


def get_meteor_shower_df(conn):
    """Returns a dataframe containing meteor shower data."""
    q = """
        SELECT 
            meteor_shower_id,
            meteor_shower_name,
            shower_start,
            shower_end,
            shower_peak 
        FROM meteor_shower
        """
    rows = query_db(conn, q, [])
    return rows


def meteor_timeline(meteor_df):

    items = []
    for item in meteor_df:
        items.append({
            "id": int(item["meteor_shower_id"]),
            "content": item["meteor_shower_name"],
            "start": str(item["shower_start"]),
            "end": str(item["shower_end"])
        })

    timeline = st_timeline(items=items,
                           groups=[], options={}, height="300px")
    st.subheader("Selected Meteor Shower")
    st.markdown(f"*{timeline["content"].capitalize()}*")


def app():
    """Layout of page 2 of the dashboard."""
    load_dotenv()
    connection = get_connection()

    st.title("Weekly trends")
    st.write("This is Page 2.")
    st.write("You can add more content here!")

    sunrise_sunset_df = get_sunrise_sunset_df(connection)
    st.write(sunrise_sunset_df)

    weather_status_df = get_weather_status_week_df(connection)
    st.write(weather_status_df)

    meteor_shower_dict = get_meteor_shower_df(connection)
    meteor_shower_df = pd.DataFrame(meteor_shower_dict)
    st.write(meteor_shower_df)

    st.write("Meteor shower timeline")
    meteor_timeline(meteor_shower_dict)


if __name__ == "__main__":
    app()
