# Daily Pipeline

This directory contains the files needed to setup the daily pipeline. It extracts astronomy information aswell as starcharts, moon phases and the nasa image of the day. It does this for every city in the city table of the database.

## Requirements

## Setup Instructions

This pipeline requires that the postgreSQL database be up and running, see ```/database``` for setup instructions.

You will need a ```.env``` file containing the following information regarding your postgreSQL database:
```
DB_HOST=[Your database host name]
DB_PORT=[Your database port]
DB_PASSWORD=[Your database password]
DB_USER=[Your database username]
DB_NAME=[Name of your db]
```

Use ```pip install -r requirements.txt```

You can now run the pipeline locally, but extra steps are required to get it running on the cloud.

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Then, use terraform init and terraform apply to create an AWS ECR and lambda function. Then, you can build and upload a docker image to the ECR. When building, use ```--provenance=false``` and the appropriate ```-platform``` argument. An AWS step function should be used to schedule the lambda function to occur once a day.

## Additional Information