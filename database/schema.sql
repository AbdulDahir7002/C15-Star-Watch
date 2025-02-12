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

CREATE TABLE country (
    country_id SMALLINT PRIMARY KEY NOT NULL,
    country_name VARCHAR NOT NULL
);

CREATE TABLE aurora_status (
    aurora_status_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    aurora_hourly_status_at TIMESTAMP NOT NULL,
    camera_visibility BOOLEAN NOT NULL,
    naked_eye_visibility BOOLEAN NOT NULL,
    country_id SMALLINT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
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
    subscriber_email VARCHAR,
    subscriber_phone VARCHAR
);

CREATE TABLE subscriber_city_assignment (
    subscriber_city_assignment_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    subscriber_id INT NOT NULL,
    city_id SMALLINT NOT NULL,
    FOREIGN KEY (subscriber_id) REFERENCES subscriber(subscriber_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE stargazing_status (
    stargazing_status_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    city_id SMALLINT NOT NULL,
    moon_phase_id SMALLINT NOT NULL,
    sunrise TIMESTAMP NOT NULL,
    sunset TIMESTAMP NOT NULL,
    status_date DATE NOT NULL,
    star_chart_url VARCHAR NOT NULL,
    moon_phase_url VARCHAR,
    nasa_apod_url VARCHAR,
    FOREIGN KEY (city_id) REFERENCES city(city_id),
    FOREIGN KEY (moon_phase_id) REFERENCES moon_phase(moon_phase_id)
);

CREATE TABLE meteor_shower_assignment (
    meteor_shower_assignment_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    meteor_shower_id SMALLINT NOT NULL,
    stargazing_status_id SMALLINT NOT NULL,
    FOREIGN KEY (meteor_shower_id) REFERENCES meteor_shower(meteor_shower_id),
    FOREIGN KEY (stargazing_status_id) REFERENCES stargazing_status(stargazing_status_id)
);