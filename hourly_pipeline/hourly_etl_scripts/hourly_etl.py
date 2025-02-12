"""Script to extract, transform and load weather data and aurora updates"""
from dotenv import load_dotenv

from aurora_status import get_connection, get_country_dict, get_current_aurora_data, get_status_per_country, insert_values_to_db

from weather_extract import get_openmeteo, get_locations, get_dates, handle_locations, clear_weather_table, insert_into_db

if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    # Aurora data
    status_dict = get_current_aurora_data()
    country_list = get_country_dict(conn)
    country_status_list = get_status_per_country(status_dict, country_list)
    insert_values_to_db(conn, country_status_list)
    conn.close()

    # Weather data
    open_meteo = get_openmeteo()
    locations = get_locations(conn)
    today_str, week_str = get_dates()
    data = handle_locations(locations, open_meteo, today_str, week_str)
    # clear_weather_table(conn)
    insert_into_db(data, conn)
    conn.close()
