# DATABASE

This directory contains files needed for the postgreSQL database.

## Requirements

All requirements are listed in requirements.txt, but the requirements for this folder specifically are:

- beautifulsoup4
- psycopg2
- python-dotenv

## Setup Instructions

Use ```pip install -r requirements.txt```

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Use terraform init, then terraform apply to create the RDS.

You will need a ```.env``` file containing the following information regarding your postgreSQL database:
```
DB_HOST=[Your database host name]
DB_PORT=[Your database port]
DB_PASSWORD=[Your database password]
DB_USER=[Your database username]
DB_NAME=[Name of your db]
```

To apply the schema to the database, use:
```
source .env
psql -h $DB_HOST -U $DB_USERNAME -f db_sql/schema.db_sql
``` 

Now that the database contains the required tables, use ```python db_scripts/seeding.py```. This will populate the country, city and meteor_shower tables.