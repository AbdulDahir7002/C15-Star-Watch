# Daily Pipeline

This directory contains the files needed to setup the daily pipeline. It extracts astronomy information aswell as starcharts, moon phases and the nasa image of the day. It does this for every city in the city table of the database.

## Requirements

The requirements for this directory are listed in ```requirements.txt```

## Setup Instructions

Before running or deploying the pipelines, make sure your ```database``` has been set up. Ensure you have followed the initial steps in the root ```README.md```. You should have a python environment with requirements installed and a ```.env``` files containing variables. This directory requires an [Astronomy API](https://docs.astronomyapi.com/) auth key.

Use ```pip install -r requirements.txt```

You can now run the pipeline locally, but extra steps are required to get it running on the cloud.

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```

Use ```first_week.py``` first to get the next seven days of data.
Then, use terraform init and terraform apply to create an AWS ECR and lambda function. Then, you can build and upload a docker image to the ECR.
Inside ```hourly_etl_scripts```, use the commands that AWS gives you to push to the registry.
When building, use ```--provenance=false``` and the appropriate ```-platform``` argument.
An AWS step function should be used to schedule the lambda function to occur once a day.

## Additional Information

```first_week.py``` gets the next seven days of data. ```daily_etl.py``` gets the data for the next day 8 days from the current date. This is the one that is used for the pipeline.