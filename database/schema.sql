DROP DATABASE IF EXISTS starwatch;

CREATE DATABASE starwatch;

\c starwatch;

CREATE TABLE meteor_shower (
    meteor_shower_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    meteor_shower_name VARCHAR NOT NULL,
    shower_start DATE NOT NULL,
    shower_end DATE NOT NULL
);

CREATE TABLE moon_phase (
    moon_phase_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    moon_phase_name VARCHAR NOT NULL
);

CREATE TABLE aurora_status (
    aurora_status_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    aurora_status_colour VARCHAR NOT NULL,
    aurora_status_desc TEXT NOT NULL
);

CREATE TABLE country (
    country_id SMALLINT PRIMARY KEY NOT NULL,
    country_name VARCHAR NOT NULL
);

CREATE TABLE city (
    city_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    city_name VARCHAR NOT NULL,
    country_id SMALLINT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    elevation FLOAT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE weather_status (
    weather_status_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    city_id SMALLINT NOT NULL,
    temperature FLOAT NOT NULL,
    coverage FLOAT NOT NULL,
    visibility FLOAT NOT NULL,
    status_at TIMESTAMP NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE subscriber (
    subscriber_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    subscriber_name VARCHAR NOT NULL,
    subscriber_email VARCHAR,
    subscriber_phone VARCHAR,
    city_id SMALLINT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE stargazing_status (
    stargazing_status_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    city_id SMALLINT NOT NULL,
    moon_phase_id SMALLINT NOT NULL,
    aurora_status_id SMALLINT NOT NULL,
    sunrise TIMESTAMP NOT NULL,
    sunset TIMESTAMP NOT NULL,
    status_date DATE NOT NULL,
    star_chart_url VARCHAR NOT NULL,
    meteor_shower_id SMALLINT NOT NULL,
    moon_phase_url VARCHAR,
    picture_of_day VARCHAR,
    FOREIGN KEY (city_id) REFERENCES city(city_id),
    FOREIGN KEY (moon_phase_id) REFERENCES moon_phase(moon_phase_id),
    FOREIGN KEY (aurora_status_id) REFERENCES aurora_status(aurora_status_id),
    FOREIGN KEY (meteor_shower_id) REFERENCES meteor_shower(meteor_shower_id)
);