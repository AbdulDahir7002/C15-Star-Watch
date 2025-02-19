# Weekly Report

This directory contains the scripts for the weekly report function of the project.

## Requirements

The requirements for this directory are listed in ```requirements.txt```

## Setup Instructions

Before running or deploying this feature, make sure your ```database``` and both ```pipelines``` have been set up. The ```dashboard``` should also be running so that users can subscribe with the subscriber page. Ensure you have followed the initial steps in the root ```README.md```. You should have a python environment with requirements installed and a ```.env``` files containing variables.

Use ```pip install -r requirements.txt```

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Then, use terraform init and terraform apply to create an AWS ECR and lambda function. Then, you can build and upload a docker image to the ECR.
Use the commands that AWS gives you to push to the registry.
When building, use ```--provenance=false``` and the appropriate ```-platform``` argument.
An AWS step function should be used to schedule the lambda function to occur once a week.
