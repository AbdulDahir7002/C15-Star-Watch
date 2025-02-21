# Hourly Pipeline

The hourly pipeline extracts weather data and aurora data from two APIs before uploading them to a postgreSQL database.

## Requirements

Requirements for this directory are listed in ```/hourly_etl_scripts/requirements.txt```

## Setup Instructions

Before running or deploying the pipelines, make sure your ```database``` has been set up. Ensure you have followed the initial steps in the root ```README.md```. You should have a python environment with requirements installed and a ```.env``` files containing variables.

You can now run the python files locally. To deploy to the cloud as an hourly pipeline, more steps are required.

In ```/terraform```, create a ```terraform.tfvars``` folder. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Then, use terraform init and terraform apply to create an AWS ECR and lambda function. Then, you can build and upload a docker image to the ECR.
Inside ```hourly_etl_scripts```, use the commands that AWS gives you to push to the registry.
When building, use ```--provenance=false``` and the appropriate ```-platform``` argument.
An AWS step function should be used to schedule the lambda function to occur once an hour.

## Additional Information

The pipeline extracts weather data for every city in the city table of the database. It finds hourly temperature, cloud cover and visibility data starting on the current day and ending a week from now.
The aurora information uses the countries in the country table of the database.