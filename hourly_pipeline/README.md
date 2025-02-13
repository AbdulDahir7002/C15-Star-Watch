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

A ```.env``` file is required containing the Amazon RDS credentials. The variable names should be: ```DB_HOST```, ```DB_PORT```, ```DB_USERNAME```, ```DB_PASSWORD```, ```DB_NAME```.

To run on the cloud, first use terraform to creat an Amazon ECR. Then, you can build and upload a docker image. When building, use ```--provenance=false``` and the appropriate ```-platform``` argument. An AWS Lambda function should point to this image URI. The function should be scheduled to occur once an hour.