"""Page 1 of the Dashboard"""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2.extras
import streamlit as st
import pandas as pd
import psycopg2
from streamlit_timeline import st_timeline
import altair as alt
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

# Data fetch


def get_avg_sunrise_sunset_df(conn):
    """Returns a dataframe containing sunrise and sunset data."""
    q = """
            SELECT 
                to_timestamp(AVG(extract( epoch FROM s.sunrise))) as sunrise,
                to_timestamp(AVG(extract( epoch FROM s.sunset))) as sunset, 
                s.status_date 
            FROM stargazing_status AS s
            JOIN city as c USING (city_id)
            GROUP BY
                s.status_date;
            """
    rows = query_db(conn, q, [])
    if len(rows) == 0:
        return pd.DataFrame(columns=["sunrise", "sunset", "status_date"])
    sunrise_sunset_df = pd.DataFrame(rows)
    sunrise_sunset_df["sunrise"] = sunrise_sunset_df["sunrise"].dt.time
    sunrise_sunset_df["sunset"] = sunrise_sunset_df["sunset"].dt.time
    return sunrise_sunset_df


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
            w.status_at <= CURRENT_DATE + INTERVAL '7 days'; 
        """
    rows = query_db(conn, q, [])
    if len(rows) == 0:
        return pd.DataFrame(columns=["weather_status_id", "city_name", "temperature",
                                     "coverage", "visibility", "status_at"])
    return pd.DataFrame(rows)


def get_meteor_shower_data(conn) -> list[dict]:
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
    if len(rows) == 0:
        return [{}]

    return rows


def get_aurora_status_df(conn):
    q = """
        SELECT 
            a.aurora_status_id,
            a.aurora_status_at,
            a.camera_visibility,
            a.naked_eye_visibility,
            c.country_name
        FROM aurora_status AS a
        JOIN country AS c USING (country_id)
        WHERE
            a.aurora_status_at > CURRENT_DATE - INTERVAL '3 days'
        """
    rows = query_db(conn, q, [])
    if len(rows) == 0:
        return pd.DataFrame(columns=["aurora_status_id", "aurora_status_at", "camera_visibility",
                                     "naked_eye_visibility", "country_name"])
    aurora_df = pd.DataFrame(rows)
    aurora_df["aurora_vis"] = sum([aurora_df["camera_visibility"],
                                   aurora_df["naked_eye_visibility"]])
    return aurora_df

# Visualisations


def meteor_timeline(meteor_df: pd.DataFrame):
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
    if timeline is None:
        st.write(f"*Select a meteor shower for details*")
    else:
        st.markdown(f"*{timeline["content"].capitalize()}*")
        st.write(f"Date range: {timeline["start"]} - {timeline["end"]}")
        # TODO: return more details


def sunrise_sunset_line(sunrise_sunset_dataframe: pd.DataFrame):
    ss_line = alt.Chart(sunrise_sunset_dataframe).mark_line().encode(
        alt.X("status_date"),
        alt.Y("sunrise"))
    st.altair_chart(ss_line)
    # TODO: Fix the output by making the y-axis time (not datetime or epoch)


def aurora_status_timeline(aurora_df: pd.DataFrame):
    aurora_line = alt.Chart(aurora_df).mark_line().encode(
        alt.X("aurora_status_at"),
        alt.Y("aurora_vis"),
        color="country_name"
    )
    st.altair_chart(aurora_line)


def app():
    """Layout of page 2 of the dashboard."""
    load_dotenv()
    connection = get_connection()

    st.title("Weekly trends")
    st.write("This is Page 2.")
    st.write("You can add more content here!")

    avg_sunrise_sunset_df = get_avg_sunrise_sunset_df(connection)
    # st.write(avg_sunrise_sunset_df)

    sunrise_sunset_line(avg_sunrise_sunset_df)

    weather_status_df = get_weather_status_week_df(connection)
    st.write(weather_status_df)

    meteor_shower_dict = get_meteor_shower_data(connection)
    meteor_shower_df = pd.DataFrame(meteor_shower_dict)
    # st.write(meteor_shower_df)

    st.markdown("## Meteor shower timeline")
    meteor_timeline(meteor_shower_dict)

    st.write("Aurora Data")
    aurora_dataframe = get_aurora_status_df(connection)
    # st.write(aurora_dataframe)

    aurora_status_timeline(aurora_dataframe)


if __name__ == "__main__":
    app()
