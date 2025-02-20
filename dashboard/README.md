# Dashboard

This directory containes the script for the streamlit dashboard as well as the terraform files required to create the appropriate cloud resourcse.

## Requirements

## Setup Instructions

Use ```pip install -r requirements.txt```

The dashboard requires that the database be up and running, see ```/database``` for setup instructions.

You will need a ```.env``` file containing the following information regarding your postgreSQL database:
```
DB_HOST=[Your database host name]
DB_PORT=[Your database port]
DB_PASSWORD=[Your database password]
DB_USER=[Your database username]
DB_NAME=[Name of your db]
```

The dashboard can now be ran locally by using ```streamlit run main.py```, but more steps are required to run it on the cloud.

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Use terraform init, then terraform apply to create the EC2. 

The dashboard scripts is automatically deployed to the EC2 instance after new changes are merged with the main repository branch