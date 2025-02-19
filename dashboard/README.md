# Dashboard

This directory contains the script for the StreamLit dashboard as well as the terraform files required to create the appropriate cloud resources.

## Requirements

The requirements for this directory are listed in ```requirements.txt```

## Setup Instructions

Before running or deploying the dashboard, make sure your ```database``` and both ```pipelines``` has been set up. Ensure you have followed the initial steps in the root ```README.md```. You should have a python environment with requirements installed and a ```.env``` files containing variables. This directory uses a [NASA APOD](https://data.nasa.gov/Space-Science/Astronomy-Picture-of-the-Day-API/ez2w-t8ua/about_data) key.

Use ```pip install -r requirements.txt```

The dashboard can now be ran locally by using ```streamlit run main.py```, but more steps are required to run it on the cloud.

In ```/terraform```, create a file called ```terraform.tfvars```. It should contain the following variables:
```
REGION = "[Your desired aws region]"
AWS_SECRET_ACCESS_KEY = "[Your aws secret key]"
AWS_ACCESS_KEY = "[your aws access key]"
```
Use terraform init, then terraform apply to create the EC2. 

The dashboard scripts are automatically deployed to the EC2 instance after changes are merged with the main repository branch.