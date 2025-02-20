"""Script that generates the weekly report for each city."""

from os import environ
from datetime import datetime
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor
import altair as alt


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
            "days": f"will reach it's peak in {row['days']} days."
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
        {"shower_name": row["meteor_shower_name"].title(), "days": f"will start in {row['days']} days."} for row in rows]
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
        {"shower_name": row["meteor_shower_name"].title(), "days": f"will end in {row['days']} days."} for row in rows]
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
    if sunrise_set_df.empty:
        return sunrise_set_df
    sunrise_set_df["sunrise"] = sunrise_set_df["sunrise"].astype(
        str).str.replace(":00", "")
    sunrise_set_df["sunset"] = sunrise_set_df["sunset"].astype(
        str).str.replace(":00", "")
    sunrise_set_df = sunrise_set_df.set_index("weekday")
    sunrise_set_df = sunrise_set_df.transpose()
    return sunrise_set_df


def average_coverage_graph(conn, city):
    """Returns a line graph showing average coverage per day."""
    q = """
    SELECT ROUND(avg(coverage)) AS coverage, TO_CHAR(w.status_at, 'Day') AS date, CAST(EXTRACT(ISODOW FROM w.status_at) AS integer) AS day_number
    FROM stargazing_status ss
    JOIN weather_status AS w 
    ON w.city_id = ss.city_id
    JOIN city AS c
    ON w.city_id = c.city_id
    WHERE c.city_name = '%s'
    AND w.status_at > sunset
    GROUP BY TO_CHAR(w.status_at, 'Day'), day_number
    ORDER BY day_number;

    """ % (city)

    cur = conn.cursor()
    cur.execute(q)
    average_coverage_df = pd.DataFrame(cur.fetchall())
    graph = alt.Chart(average_coverage_df).mark_line().encode(
        x=alt.X("day_number:O"),
        y="coverage:Q").properties(width=535, height=535)
    with open("/tmp/average_coverage_graph.png", "wb") as f:
        graph.save(f, format="png", ppi=100)


def average_visibility_graph(conn, city):
    """Returns a line graph showing average coverage per day."""
    q = """
    SELECT ROUND(avg(visibility)) AS visibility, TO_CHAR(w.status_at, 'Day') AS date, CAST(EXTRACT(ISODOW FROM w.status_at) AS integer) AS day_number
    FROM stargazing_status ss
    JOIN weather_status AS w 
    ON w.city_id = ss.city_id
    JOIN city AS c
    ON w.city_id = c.city_id
    WHERE c.city_name = '%s'
    AND w.status_at > sunset
    GROUP BY TO_CHAR(w.status_at, 'Day'), day_number
    ORDER BY day_number;

    """ % (city)

    cur = conn.cursor()
    cur.execute(q)
    average_coverage_df = pd.DataFrame(cur.fetchall())
    graph = alt.Chart(average_coverage_df).mark_line().encode(
        x=alt.X("day_number:O"),
        y="visibility:Q").properties(width=535, height=535)

    with open("/tmp/average_visibility_graph.png", "wb") as f:
        graph.save(f, format="png", ppi=100)


def highest_coverage_day(conn, city):
    """Returns day with highest coverage."""
    q = """
        SELECT ROUND(avg(coverage)) AS coverage, TO_CHAR(w.status_at, 'Day') AS date
        FROM stargazing_status ss
        JOIN weather_status AS w 
        ON w.city_id = ss.city_id
        JOIN city AS c
        ON w.city_id = c.city_id
        WHERE c.city_name = '%s'
        AND w.status_at > sunset
        GROUP BY TO_CHAR(w.status_at, 'Day')
        ORDER BY coverage ASC 
        LIMIT 1
        ;
    """ % (city)

    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    if rows == []:
        return "No data"
    return rows[0]["date"].title()


def highest_visibility_day(conn, city):
    """Returns day with highest coverage."""
    q = """
        SELECT ROUND(avg(visibility)) AS visibility, TO_CHAR(w.status_at, 'Day') AS date
        FROM stargazing_status ss
        JOIN weather_status AS w 
        ON w.city_id = ss.city_id
        JOIN city AS c
        ON w.city_id = c.city_id
        WHERE c.city_name = '%s'
        AND w.status_at > sunset
        GROUP BY TO_CHAR(w.status_at, 'Day')
        ORDER BY visibility DESC 
        LIMIT 1
        ;
    """ % (city)

    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    if rows == []:
        return "No data"
    return rows[0]["date"].title()


def best_stargazing_day(conn, city):
    """Returns the best day to go stargazing with visibility and coverage information."""
    q = """
        WITH coverage_rank as(
    SELECT ROUND(avg(w.coverage)) AS coverage, TO_CHAR(w.status_at, 'Day') AS date, RANK() OVER (ORDER BY AVG(w.coverage) ASC) AS c_rank
    FROM stargazing_status ss
    JOIN weather_status AS w 
    ON w.city_id = ss.city_id
    JOIN city AS c
    ON w.city_id = c.city_id
    WHERE c.city_name = '%s'
    AND w.status_at > sunset
    GROUP BY TO_CHAR(w.status_at, 'Day')
    ORDER BY coverage ASC 
    ),
    visibility_rank AS (
    SELECT ROUND(avg(w.visibility)) AS visibility, TO_CHAR(w.status_at, 'Day') AS date, RANK() OVER (ORDER BY AVG(w.visibility) desc) AS v_rank
    FROM stargazing_status ss
    JOIN weather_status AS w 
    ON w.city_id = ss.city_id
    JOIN city AS c
    ON w.city_id = c.city_id
    WHERE c.city_name = '%s'
    AND w.status_at > sunset
    GROUP BY TO_CHAR(w.status_at, 'Day')
    ORDER BY visibility ASC 
    )
    SELECT c.c_rank * v.v_rank AS RANK ,c.coverage, v.visibility, c.date
    FROM coverage_rank AS c
    JOIN visibility_rank AS v
    ON v.date = c.date
    ORDER BY RANK ASC
    LIMIT 1;
    """ % (city, city)
    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchone()
    if rows is None:
        return {"day": "", "visibility": "", "coverage": ""}
    return {"day": rows["date"], "visibility": int(rows["visibility"]), "coverage": int(rows["coverage"])}


def format_template(conn, city):
    """Returns the formatted template."""
    environment = Environment(loader=FileSystemLoader("."))
    template = environment.get_template("report_frame.html")

    meteor_info = combine_meteor_info(get_meteor_peak(
        conn), get_starting_meteors(conn), get_ending_meteors(conn))

    if meteor_info == []:
        meteor_info = [
            {"shower_name": "", "days": "There are no meteor events happening this week!"}]

    average_coverage_graph(conn, city)
    average_visibility_graph(conn, city)
    best_stargazing_day_info = best_stargazing_day(conn, city)

    context = {
        "city": city,
        "date": datetime.now().strftime('%d-%m-%Y'),
        "meteor_shower_info": meteor_info,
        "day_of_the_week": "Chewsday",
        "table": sunrise_set_df(conn, city).to_html(index=True, border="1px", justify="center"),
        "coverage_day": highest_coverage_day(conn, city),
        "visibility_day": highest_visibility_day(conn, city),
        "day_of_week": best_stargazing_day_info["day"],
        "visibility": best_stargazing_day_info["visibility"],
        "coverage": best_stargazing_day_info["coverage"]
    }
    return template.render(context)


def write_email(city):
    """Returns html of the report."""
    load_dotenv()
    conn = get_connection()
    html = format_template(conn, city)
    conn.close()
    return html


if __name__ == "__main__":
    write_email("London")
