DROP TABLE moon_phase;

alter table stargazing_status
drop column moon_phase_id;

alter table stargazing_status
drop column aurora_status_id;

alter table stargazing_status
drop column meteor_shower_id;

alter table stargazing_status
drop column nasa_apod_url;

alter table stargazing_status
add column nasa_apod_id;

alter table stargazing_status
add column moon_phase_url;

alter table stargazing_status
add CONSTRAINT FOREIGN KEY(nasa_apod_id) REFERENCES nasa_apod(nasa_apod_id);

alter table stargazing_status
add CONSTRAINT UNIQUE(city_id, moon_phase_id, sunrise, sunset, status_date, star_chart_url, moon_phase_url, nasa_apod_id);