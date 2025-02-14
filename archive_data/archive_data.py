"""Script to archive data older than a week from the database and upload to S3."""
from os import environ
from dotenv import load_dotenv
from datetime import date
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor, RealDictRow


def get_connection() -> connection:
    """Returns connection for postgres database."""
    conn = connect(dbname=environ["DB_NAME"], cursor_factory=RealDictCursor)
    return conn


def retrieve_old_meteor_shower_data(conn) -> pd.DataFrame:
    """Returns a dataframe of meteor shower data older than a week."""
    q = """
        SELECT * FROM meteor_data
        WHERE shower_end < NOW() - INTERVAL '7 days';
    """
    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    meteor_shower_df = pd.DataFrame(rows)
    return meteor_shower_df


def retrieve_old_aurora_data(conn) -> pd.DataFrame:
    """Returns a dataframe of aurora data older than a week."""
    q = """
        SELECT * FROM aurora_data
        WHERE aurora_hourly_status_at < NOW() - INTERVAL '7 days';
    """
    cur = conn.cursor()
    cur.execute(q)
    rows = cur.fetchall()
    aurora_df = pd.DataFrame(rows)
    return aurora_df


def delete_meteor_data(conn) -> str:
    """Delete meteor data older than a week."""
    q = """
        DELETE FROM meteor_shower
        WHERE shower_end < NOW() - INTERVAL '7 days';
    """
    cur = conn.cursor()
    cur.execute(q)
    conn.commit()
    return "Stale meteor data deleted!"


def delete_weather_data(conn) -> str:
    """Deletes weather data older than a week."""
    q = """
        DELETE FROM weather_status
        WHERE status_at < NOW() - INTERVAL '7 days';
    """
    cur = conn.cursor()
    cur.execute(q)
    conn.commit()
    return "Stale weather data deleted!"


def convert_to_parquet(df_name: str, df: pd.DataFrame) -> None:
    """Converts dataframe to parquet file."""
    filename = f"{df_name}_{date.today()}.parquet"
    df.to_parquet(filename)
    return "Done!"


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    print(retrieve_old_aurora_data(conn))
    print(retrieve_old_meteor_shower_data(conn))
