# DATABASE

This directory contains the files needed for the postgreSQL database.

## Requirements

This directory requires no additional requirements beyond those in the root folders ```requirements.txt```

## Setup Instructions

Before creating and populating the database, ensure you have followed the initial steps in the root ```README.md```. You should have a python environment with requirements installed and a ```.env``` files containing variables.

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Use terraform init, then terraform apply to create the RDS.

To apply the schema to the database, use:
```
source .env
psql -h $DB_HOST -U $DB_USERNAME -f db_sql/schema.sql
``` 
Then, create useful views and populate the constellations table with:
```
psql -h $DB_HOST -U $DB_USERNAME -f db_sql/views.sql
psql -h $DB_HOST -U $DB_USERNAME -f db_sql/contellations.sql
``` 

Now that the database contains the required tables, use ```python db_scripts/seeding.py```. This will populate the country, city and meteor_shower tables. You can now setup the pipelines (```hourly_pipeline``` and ```daily_pipeline```).