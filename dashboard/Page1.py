"""Page 1 of the dashboard."""
from os import environ as ENV
from datetime import date, timedelta
import logging
import sys

import requests
import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv


def configure_logs():
    """Configure the logs for the whole project to refer to"""

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        handlers=[
            logging.FileHandler("logs/pipeline.log", mode="a",
                                encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )


@st.cache_resource
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


@st.cache_data
def get_cities() -> list:
    """Gets a list of cities from the database."""
    connection = get_connection()
    with connection.cursor() as curs:
        curs.execute("SELECT city_name FROM city;")
        cities = [city[0] for city in curs.fetchall()]
    return cities


@st.cache_data
def get_constellations() -> list:
    """Gets a list of constellations from the database."""
    connection = get_connection()
    with connection.cursor() as curs:
        curs.execute("SELECT constellation_name FROM constellation;")
        constellations = [constellation[0]
                          for constellation in curs.fetchall()]
    return constellations


def get_constellation_code(constellation: str) -> str:
    """Gets the code that identifies the constellation."""
    connection = get_connection()
    query = """
            SELECT constellation_code
            FROM constellation
            WHERE constellation_name = %s;
            """
    with connection.cursor() as curs:
        curs.execute(query, [constellation])
        constellation = curs.fetchone()[0]
    return constellation


@st.cache_data
def get_country(city: str) -> int:
    """Returns the country ID for a given city."""
    connection = get_connection()
    with connection.cursor() as curs:
        curs.execute(
            "SELECT country_id FROM city WHERE city_name = %s;", [city])
        country_id = curs.fetchone()[0]
    return country_id


@st.cache_data(ttl=3600)
def get_aurora_info(country_id: int) -> pd.DataFrame:
    """Returns the aurora data for given country."""
    logging.info("Fetching requested aurora data...")
    connection = get_connection()

    with connection.cursor() as curs:
        curs.execute(
            f"SELECT * FROM aurora_status WHERE country_id = '{country_id}';")
        aurora_data = curs.fetchall()
        logging.info("Fetched!")
        data = {
            'Recording At': [str(aurora_data[-1][1])],
            'Visible by Camera': [str(aurora_data[-1][2])],
            'Visible by Eye': [str(aurora_data[-1][3])]
        }
    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def get_weather_for_day(day: date, city: str) -> pd.DataFrame:
    """Returns weather information given a city and a day."""
    logging.info("Fetching requested weather data...")
    connection = get_connection()
    query = """
            SELECT *
            FROM weather_status
            JOIN city ON (city.city_id = weather_status.city_id)
            WHERE city_name = %s
            AND status_at >= %s
            AND status_at <= %s;
            """
    with connection.cursor() as curs:
        curs.execute(query, [city, day, str(day)+' 23:59'])

        weather_data = [(str(weather[5]).split(" ")[1][:2],
                         round(weather[2], 1),
                         str(weather[3]).split('.', maxsplit=1)[0],
                         str(weather[4]).split('.', maxsplit=1)[0])
                        for weather in curs.fetchall()]

    data = pd.DataFrame(weather_data)
    logging.info("Fetched!")
    data.columns = ['Time', 'Temperature', 'Coverage', 'Visibility']
    data = data[data['Time'].isin(['00', '06', '12', '18', '23'])]
    data = data.T
    data.index = ['Time', 'Temperature', 'Coverage', 'Visibility']
    return data


@st.cache_data(ttl=3600)
def get_weather_for_week(city: str) -> pd.DataFrame:
    """Returns the weekly weather forecast of a city."""
    connection = get_connection()
    query = """
            SELECT *
            FROM weather_status
            JOIN city ON (city.city_id = weather_status.city_id)
            WHERE city_name = %s;
            """
    with connection.cursor() as curs:
        curs.execute(query, [city])

        weather_data = [(weather[5],
                         round(weather[2], 1),
                         float(str(weather[3]).split('.', maxsplit=1)[0]),
                         float(str(weather[4]).split('.', maxsplit=1)[0]))
                        for weather in curs.fetchall()]

    weather_data = pd.DataFrame(weather_data)
    weather_data.columns = ['Time', 'Temperature', 'Coverage', 'Visibility']
    return weather_data


@st.cache_data(ttl=86400)
def get_stargazing_status_for_day(day: date, city: str) -> list:
    """Returns stargazing information given a city and a day."""
    logging.info("Fetching requested star chart...")
    connection = get_connection()
    query = """
            SELECT stargazing_status.*, city_name
            FROM stargazing_status JOIN city
            ON (city.city_id = stargazing_status.city_id)
            WHERE city_name = %s
            AND status_date = %s;
            """

    with connection.cursor() as curs:
        curs.execute(query, [city, day])
        stargazing_status = curs.fetchone()

    return stargazing_status


@st.cache_data(ttl=86400)
def get_stargazing_status_for_week(city: str) -> list:
    """Gets stargazing weekly forecast for a city"""
    connection = get_connection()
    query = """
            SELECT stargazing_status.*, city_name
            FROM stargazing_status JOIN city
            ON (city.city_id = stargazing_status.city_id)
            WHERE city_name = %s
            AND status_date >= %s;
            """
    with connection.cursor() as curs:
        curs.execute(query, [city, date.today()])
        results = curs.fetchall()

    return results


def get_meteor_showers_for_day(day) -> pd.DataFrame:
    """Gets meteor showers occurring during given day."""
    logging.info("Fetching requested meteor shower data...")
    connection = get_connection()
    query = """
            SELECT *
            FROM meteor_shower
            WHERE %s >= shower_start
            AND %s <= shower_end;
            """
    with connection.cursor() as curs:
        curs.execute(query, [day, day])
        results = curs.fetchall()

    df = pd.DataFrame(results)
    logging.info("Fetched!")
    if len(results) > 0:
        df.columns = ["id", "Name", "Start Date", "End Date", "Peak Date"]
        return df

    return None


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
    return '&#9728;'


def get_days() -> list:
    """Returns a list of dates from today to a week from now."""
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]
    days.append("Week")
    return days


def column_one(weather: pd.DataFrame) -> None:
    """Writes info intended for left column."""
    if weather is None:
        st.write("No weather for this date/location.")
    else:
        emoji = get_emoji_for_weather(weather)
        st.markdown(f'<h3>Weather Forecast {emoji}</h3>',
                    unsafe_allow_html=True)
        weather = weather.reset_index()
        weather.columns = ['Time', 'Midnight', '6 AM', 'Noon', '6 PM', '11 PM']
        weather = weather.iloc[1:]
        st.table(weather)


def column_two(star_status: list) -> None:
    """Writes info intended for right column."""
    st.markdown("<h3>Sunset / Sunrise &#9728;</h3>",
                unsafe_allow_html=True)
    if star_status is None:
        st.write("No data for this date/location.")
    else:
        st.write("Sunrise: ", date.strftime(star_status[2], '%H:%M'), 'AM')
        st.write("Sunset: ", date.strftime(star_status[3], '%H:%M'), 'PM')


def column_three(star_status: list) -> None:
    """Defines the code in column three."""
    st.markdown("<h3>Moonphase &#127765; </h3>", unsafe_allow_html=True)

    if star_status is None:
        st.write("No data for this date/location.")
    else:
        st.image(star_status[6])


def column_four(showers: pd.DataFrame) -> None:
    """Defines the code in column four."""
    st.markdown("<h3>Meteor showers &#9732; </h3>", unsafe_allow_html=True)

    if showers is None:
        st.write("No meteor showers on this day.")
    else:
        showers.columns = [' ', 'Name', 'Start Date', 'End Date', 'Peak Date']
        st.table(showers)


def weather_charts(weather: pd.DataFrame) -> None:
    """Adds the weather charts to the dashboard."""
    st.write('Data for the next 7 days.')
    with st.container(border=True):
        st.markdown("<h3>Temperature</h3>", unsafe_allow_html=True)
        st.line_chart(weather.set_index('Time'), y=['Temperature'])
    with st.container(border=True):
        st.markdown("<h3>Visibility</h3>", unsafe_allow_html=True)
        st.line_chart(weather.set_index('Time'), y=['Visibility'])
    with st.container(border=True):
        st.markdown("<h3>Cloud Coverage</h3>", unsafe_allow_html=True)
        st.line_chart(weather.set_index('Time'), y=['Coverage'])


def post_location_get_starchart(header: str,
                                lat: float,
                                long: float,
                                date_to_query: str,
                                code: str) -> str:
    """Returns the url of a star chart for specific coordinates."""
    body = {
        "style": "default",
        "observer": {
            "latitude": lat,
            "longitude": long,
            "date": str(date_to_query)
        },
        "view": {
            "type": "constellation",
            "parameters": {
                "constellation": code
            }
        }
    }

    response = requests.post(
        "https://api.astronomyapi.com/api/v2/studio/star-chart",
        headers={'Authorization': header},
        json=body,
        timeout=60
    )

    return response.json()['data']['imageUrl']


def get_lat_and_long(city: str) -> tuple:
    """Gets the latitude and longitude of a given city."""
    connection = get_connection()
    query = """
            SELECT latitude, longitude
            FROM city
            WHERE city_name = %s;
            """
    with connection.cursor() as curs:
        curs.execute(query, [city])
        results = curs.fetchall()

    return results[0][0], results[0][1]


def create_scroll_image(url: str, height: int) -> None:
    """Uses the link to make a pan/zoom image."""
    st.components.v1.html(
        f"""
    <div id="openseadragon1" style="width: 90%; height: {height}px; margin-left: auto; margin-right: auto;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/3.1.0/openseadragon.min.js"></script>
    <script>
        var viewer = OpenSeadragon({{
            id: "openseadragon1",
            prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/3.1.0/images/",
            tileSources: {{
                type: 'image',
                url: '{url}'
            }},
            minZoomLevel: 1,
            maxZoomLevel: 10,
            defaultZoomLevel: 1
        }});
    </script>
    """,
        height=height,
    )


def app():
    """The function ran when the user switches to this page."""
    load_dotenv()

    configure_logs()

    HEADER = f'Basic {ENV["ASTRONOMY_BASIC_AUTH_KEY"]}'

    city = st.sidebar.selectbox('City', get_cities())
    country_id = get_country(city)
    day = st.sidebar.selectbox('Day', get_days())
    if day != 'Week':
        showers = get_meteor_showers_for_day(day)
        weather = get_weather_for_day(day, city)
        star_status = get_stargazing_status_for_day(day, city)
    else:
        weather = get_weather_for_week(city)
        star_status = get_stargazing_status_for_week(city)
    aurora = get_aurora_info(country_id)
    st.title("Forecast")
    st.write("""Please choose the city you would like the forecast for on the left, future dates up to a week are also available. 
             You can also select 'week' to show general trends for the upcoming week.""")
    st.markdown(f"## {city}")

    if day != 'Week':
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True, height=240):
                column_one(weather)
        with col2:
            with st.container(border=True, height=240):
                column_two(star_status)

        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True, height=400):
                column_three(star_status)
        with col4:
            with st.container(border=True, height=400):
                column_four(showers)

        with st.container(border=True):
            st.markdown(
                '<h3 style="text-align: center;">Starchart &#11088;</h3>', unsafe_allow_html=True)
            if star_status is None:
                st.write("No Data for this date/location.")
                logging.debug("No data found in star status")
            else:
                create_scroll_image(star_status[5], 617)

        if day == date.today():
            with st.container(border=True):
                st.markdown("<h3>Aurora Activity</h3>",
                            unsafe_allow_html=True)
                st.table(aurora)
    else:
        weather_charts(weather)
        with st.container(border=True):
            st.markdown("<h3>Moon Phases</h3>", unsafe_allow_html=True)
            columns = st.columns(8)
            data = []
            for i, status in enumerate(star_status):
                data.append((str(status[2]).split(" ", maxsplit=1)[0], str(status[2]).split(" ")[1],
                            str(status[3]).split(" ")[1]))
                with columns[i]:
                    st.image(status[6])

        sun_times = pd.DataFrame(data)
        sun_times.columns = ["Day", "Sun Rise", "Sun Set"]
        with st.container(border=True):
            st.markdown("<h3>Sunrise/set times</h3>", unsafe_allow_html=True)
            st.line_chart(sun_times.set_index('Day'))


if __name__ == "__main__":
    app()
