"""Script that generates the weekly report for each city."""

from os import environ
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor


def get_connection():
    """Gets a connection to the database"""
    connection = psycopg2.connect(host=environ["DB_HOST"],
                                  user=environ["DB_USERNAME"],
                                  dbname=environ["DB_NAME"],
                                  password=environ["DB_PASSWORD"],
                                  port=environ["DB_PORT"],
                                  cursor_factory=RealDictCursor)
    return connection


def get_all_cities(conn):
    """Returns all cities from database."""
    q = """
        SELECT city_name
        FROM city
    """
    cur = conn.cursor()
    cur.execute(q)
    cities = cur.fetchall()
    return [city["city_name"] for city in cities]


def get_meteor_peak(conn):
    """Returns dictionary of meteors that are peaking this week."""
    q = """
        SELECT meteor_shower_name, shower_peak - current_date AS days
        FROM meteor_shower
        WHERE current_date >= shower_peak - INTERVAL '7 days';
    """
    shower_info = []
    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    for row in rows:
        shower_info.append({
            "shower_name": row["meteor_shower_name"].title(),
            "days": f"will reach it's peak in {row["days"]} days."
        })
    return shower_info


def get_starting_meteors(conn):
    """Returns a dictionary of information on meteors starting in the next week."""
    q = """
        SELECT meteor_shower_name, shower_start - current_date AS days
        FROM meteor_shower
        WHERE current_date >= shower_start - INTERVAL '7 days';
    """
    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    starting_showers = [
        {"shower_name": row["meteor_shower_name"].title(), "days": f"will start in {row["days"]} days."} for row in rows]
    return starting_showers


def get_ending_meteors(conn):
    """Returns a dictionary of meteors ending this week."""
    q = """
        SELECT meteor_shower_name, shower_end - current_date AS days
        FROM meteor_shower
        WHERE current_date >= shower_end - INTERVAL '7 days';
    """
    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    ending_showers = [
        {"shower_name": row["meteor_shower_name"].title(), "days": f"will end in {row["days"]} days."} for row in rows]
    return ending_showers


def combine_meteor_info(peak: list, start: list, end: list) -> list:
    """Returns a list of all combined meteor info."""
    all_info = []
    all_info.extend(peak)
    all_info.extend(start)
    all_info.extend(end)
    return all_info


def sunrise_set_df(conn, city):
    """Returns a dataframe of sunrise and sunset information this week."""
    q = """
        SELECT TO_CHAR(sunrise, 'Day') weekday, CAST(ss.sunrise AS time), CAST(ss.sunset AS time)
        FROM stargazing_status ss 
        JOIN city AS c 
        ON c.city_id = ss.city_id
        WHERE current_date >= status_date - INTERVAL '6 days'
        AND city_name = '%s'
    """ % (city)
    cur = conn.cursor()
    cur.execute(q)
    sunrise_set_df = pd.DataFrame(cur.fetchall())
    sunrise_set_df = sunrise_set_df.transpose()
    return sunrise_set_df


def format_template(conn, city):
    """Returns the formatted template."""
    environment = Environment(loader=FileSystemLoader("."))
    template = environment.get_template("report_frame.html")
    meteor_info = combine_meteor_info(get_meteor_peak(
        conn), get_starting_meteors(conn), get_ending_meteors(conn))
    context = {
        "city": "City",
        "date": "17-02-2025",
        "meteor_shower_info": meteor_info,
        "day_of_the_week": "Chewsday",
        "table": sunrise_set_df(conn, city).to_html(index=True),
        "avg_coverage_graph": "filepath",
        "avg_visibility_graph": "filepath",
        "coverage_day": "Monday",
        "visibility_day": "Tuesday",
        "day_of_week": "Wednesday",
        "visibility": 20,
        "coverage": 100
    }
    return template.render(context)


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    html = format_template(conn, "London")
    with open("view_html.html", "w") as f:
        f.write(html)
    # print(get_all_cities(conn))
    # print(get_ending_meteors(conn))
    conn.close()
