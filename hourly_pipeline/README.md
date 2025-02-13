# Hourly Pipeline

The hourly pipeline extracts weather data and aurora data from two APIs before uploading them to a postgreSQL database.

## Requirements

All requirements are listed in requirements.txt, but the requirements for this folder specifically are:

- openmeteo-requests
- requests-cache
- pandas
- psycopg2
- retry-requests
- python-dotenv

## Setup Instructions

Use ```pip install -r requirements.txt```

You will need a ```.env``` file containing the following information regarding your postgreSQL database:
```
DB_HOST=[Your database host name]
DB_PORT=[Your database port]
DB_PASSWORD=[Your database password]
DB_USER=[Your database username]
DB_NAME=[Name of your db]
```
You can now run the python files locally.

To run on the cloud, first use terraform to create an Amazon ECR. Then, you can build and upload a docker image. When building, use ```--provenance=false``` and the appropriate ```-platform``` argument. An AWS Lambda function should point to this image URI. The function should be scheduled to occur once an hour.

## Additional Information

The pipeline extracts weather data for every city in the city table of the database. It finds hourly temperature, cloud cover and visibility data starting on the current day and ending a week from now.
The aurora information uses the countries in the country table of the database.