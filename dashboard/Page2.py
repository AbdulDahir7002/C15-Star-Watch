"""Page 1 of the Dashboard"""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2.extras
import streamlit as st
import pandas as pd
import psycopg2

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


def query_db(conn, query: str, params: tuple) -> list[tuple]:
    """Query the database and return a list of tuples of values"""
    print(conn)
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        output = cursor.fetchall()
    return output


def get_sunrise_sunset_pandas(conn):
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


def app():
    """Layout of page 2 of the dashboard"""
    load_dotenv()
    connection = get_connection()

    st.title("Page 2")
    st.write("This is Page 2.")
    st.write("You can add more content here!")

    sunrise_sunset_df = get_sunrise_sunset_pandas(connection)

    st.write(sunrise_sunset_df)


if __name__ == "__main__":
    app()
