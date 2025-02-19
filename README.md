# StarWatch

## What is this project?

StarWatch is a central location for amateur astronomers and the general public to find all they information they need for stargazing. This includes the weather, sunset and sunrise times, aurora visibility, current meteor showers and a star chart. It also includes visualisations of past data, so users can get an idea of trends in the data.
Additionally, users can opt into a weekly newsletter for their chosen location. Every week, they will receive an email containing all the information they need for stargazing.
Currently, 71 cities across the United Kingdom are supported.

The project uses Amazon Web Services.

Here is the architecture diagram:
![Architecture Diagram](/images/C15-Star-Watch-Architecture.png)

Here is the ERD diagram:
![Database Diagram](/images/C15-Star-Watch-ERD.png)

## Set Up

 - Inside the root directory, use ```python3 -m venv .venv``` and ```source .venv/bin/activate```
 - Next, do ```pip install -r requirements.txt``` to install the dependencies
 - Create an environment variables file with ```touch .env```
 - Populate ```.env``` with the following information:
```
DB_NAME=[The name of the RDS database that you create.]
DB_USERNAME=[The username for the database.]
DB_PASSWORD=[The password for the database.]
DB_HOST=[The host address for the RDS that you create.]
DB_PORT=[The port for the RDS.]
ASTRONOMY_BASIC_AUTH_KEY= [Your [Astronomy API](https://docs.astronomyapi.com/) auth key.]
NASA_APOD_KEY=[Your [NASA APOD](https://data.nasa.gov/Space-Science/Astronomy-Picture-of-the-Day-API/ez2w-t8ua/about_data) auth key.]
```

[Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) can be used to easily provision the necessary cloud infrastructure to run the project.

Each directory contains a README with detailed instructions on setting up the corresponding feature. The database is the best place to start. Head to ```/database/README.md``` for more instructions.

## Directories

### hourly_pipeline

The hourly pipeline fetches weather and aurora data. The directory contains the terraform files needed to set up the pipeline, as well as the scripts that it uses. For more information on setting it up, head to the README in the directory.

### daily_pipeline

The daily pipeline fetches astronomy information. The directory contains the terraform files needed to set up the pipeline, as well as the scripts that it uses. For more information on setting it up, head to the README in the directory.

### database

The database directory contains the terraform files and the sql files that are needed to set it up. It also includes a seeding script that will insert city and meteor shower information into the database. For more information on setting it up, head to the README in the directory.

### dashboard

The dashboard displays the information that has been gathered by the pipeline. This directory contains the terraform to set it up, as well as the scripts that it uses. For more information on setting it up, head to the README in the directory.

### weekly-report

The weekly-report is sent to subscribers, containing information regarding a location. The directory contains the terraform files needed to set it up, as well as the html template for the email and other scripts. For more information about setting it up, go to the README in the directory.