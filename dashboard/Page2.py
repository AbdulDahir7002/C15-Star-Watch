"""Page 2 of the Dashboard."""
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


@st.cache_resource(ttl=600)
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


def query_db(query: str, params: tuple) -> list[dict]:
    """Query the database and return a list of tuples of values."""
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        output = cursor.fetchall()
    return output

# Data fetch


@st.cache_data
def get_avg_sunrise_sunset_df():
    """Returns a dataframe containing sunrise and sunset data."""
    q = """
            SELECT 
                to_timestamp(AVG(extract( epoch FROM s.sunrise))) as sunrise,
                to_timestamp(AVG(extract( epoch FROM s.sunset))) as sunset, 
                s.status_date 
            FROM stargazing_status AS s
            JOIN city as c USING (city_id)
            GROUP BY
                s.status_date
            ORDER BY
                s.status_date
            ;
            """
    rows = query_db(q, [])
    if len(rows) == 0:
        return pd.DataFrame(columns=["sunrise", "sunset", "status_date"])
    sunrise_sunset_df = pd.DataFrame(rows)
    return sunrise_sunset_df


@st.cache_data
def get_weather_status_week_df():
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
    rows = query_db(q, [])
    if len(rows) == 0:
        return pd.DataFrame(columns=["weather_status_id", "city_name", "temperature",
                                     "coverage", "visibility", "status_at"])
    return pd.DataFrame(rows)


@st.cache_data
def get_meteor_shower_data() -> list[dict]:
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
    rows = query_db(q, [])
    if len(rows) == 0:
        return [{}]

    return rows


def set_aurora_vis_label(value):
    """Apply relevant aurora status depending on value"""
    if value == 0:
        return "Not visible"
    elif value == 1:
        return "Visible to cameras"
    else:
        return "Fully visible"


@st.cache_data
def get_aurora_status_df():
    """Gets aurora data and transforms it"""
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
    rows = query_db(q, [])
    if len(rows) == 0:
        return pd.DataFrame(columns=["aurora_status_id", "aurora_status_at", "camera_visibility",
                                     "naked_eye_visibility", "country_name"])
    aurora_df = pd.DataFrame(rows)
    aurora_df["aurora_vis"] = sum([aurora_df["camera_visibility"],
                                   aurora_df["naked_eye_visibility"]])
    aurora_df["aurora_vis_label"] = aurora_df["aurora_vis"].apply(
        set_aurora_vis_label)
    return aurora_df

# Visualisations


def meteor_timeline(meteor_df: pd.DataFrame):
    """Displays a timeline of currently known meteor showers"""
    items = []
    for item in meteor_df:
        items.append({
            "id": int(item["meteor_shower_id"]),
            "content": item["meteor_shower_name"],
            "start": str(item["shower_start"]),
            "end": str(item["shower_end"]),
            "peak": str(item["shower_peak"])
        })

    timeline = st_timeline(items=items,
                           groups=[], options={}, height="300px")
    st.markdown("#### Selected Meteor Shower:")
    if timeline is None:
        st.write("*Select a meteor shower for details*")
    else:
        st.markdown(f"*{timeline['content'].capitalize()}*")
        st.write(
            f"From :orange[*{timeline["start"]}*] to :orange[*{timeline["end"]}*]")
        st.write(f"Peaks on :orange[*{timeline["peak"]}*]")

        # TODO: return more details


def sunrise_sunset_line(sunrise_sunset_dataframe: pd.DataFrame):
    """Graphs sunrise and sunset over time"""
    sunrise_line = alt.Chart(sunrise_sunset_dataframe).mark_line().encode(
        alt.X("monthdate(status_date):T"),
        alt.Y("hoursminutes(sunrise):T"))
    sunset_line = alt.Chart(sunrise_sunset_dataframe).mark_line().encode(
        alt.X("monthdate(status_date):T", title="Date"),
        alt.Y("hoursminutes(sunset):T", title="Sunset"))

    col1, col2 = st.columns(2)

    with col1:
        st.altair_chart(sunrise_line)
    with col2:
        st.altair_chart(sunset_line)
    # TODO: Fix the output by making the y-axis time (not datetime or epoch)


def aurora_status_timeline(aurora_df: pd.DataFrame):
    """Maps aurora visibility over time"""
    aurora_line = alt.Chart(aurora_df).mark_line().encode(
        alt.X("aurora_status_at").title("Time"),
        alt.Y("aurora_vis_label").title("Visibility"),
        color="country_name"
    )
    st.altair_chart(aurora_line)


def aurora_status_bar_charts(aurora_df: pd.DataFrame):
    """Bar chart comparing aurora visibility for each country"""
    aurora_df = aurora_df[aurora_df["aurora_vis"] > 0]
    aurora_cam_vis = aurora_df[[
        "country_name", "naked_eye_visibility"]].value_counts().reset_index()
    aurora_cam_vis["naked_eye_visibility"] = aurora_cam_vis["naked_eye_visibility"].map(
        {True: "Camera Visible", False: "Fully Visible"})

    aurora_bar = alt.Chart(aurora_cam_vis).mark_bar().encode(
        alt.X("naked_eye_visibility").title("Visibility"),
        alt.Y("count").title("Count"),
        alt.Color("country_name", title="Country"))
    st.altair_chart(aurora_bar)


def app():
    """Layout of page 2 of the dashboard."""
    load_dotenv()

    st.title("Weekly trends")

    with st.container(border=True):
        st.markdown("### Sunrise and Sunset average over time &#9728; ")
        avg_sunrise_sunset_df = get_avg_sunrise_sunset_df()
        sunrise_sunset_line(avg_sunrise_sunset_df)

    weather_status_df = get_weather_status_week_df()

    with st.container(border=True):
        st.markdown("### Meteor shower timeline &#x2604;")
        meteor_shower_dict = get_meteor_shower_data()
        meteor_shower_df = pd.DataFrame(meteor_shower_dict)
        meteor_timeline(meteor_shower_dict)

    aurora_dataframe = get_aurora_status_df()
    with st.container(border=True):
        st.markdown("### Aurora Occurrences &#10024;")
        aurora_status_timeline(aurora_dataframe)

    with st.container(border=True):
        st.markdown("### Aurora Sighting Proportions &#10024;")
        aurora_status_bar_charts(aurora_dataframe)


if __name__ == "__main__":
    app()
