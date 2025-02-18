"""Function to send an email using boto3."""

import re
from dotenv import load_dotenv
from os import environ
from boto3 import client
from botocore.exceptions import ClientError

from weekly_report_generator import write_email, get_all_cities, get_connection


def list_all_topics(sns: client):
    """Returns a list of all topics on AWS."""
    response = sns.list_topics()
    topics = []
    while True:
        topics.extend(response["Topics"])
        if "NextToken" in response:
            response = sns.list_topics(NextToken=response["NextToken"])
        else:
            break
    return [topic["TopicArn"] for topic in topics]


def list_relevant_topics(all_topics: list) -> list:
    """Returns a list of starwatch topics on AWS."""
    topics = all_topics
    starwatch_topics = [name for name in topics if re.search(
        "(c15-star-watch-)(.*)", name)]
    return starwatch_topics


def retrieve_chosen_topic(topic_list: list, city: str) -> str:
    """Returns the topic arn the user has chosen to subscribe to."""
    chosen_topic = [topic for topic in topic_list if bool(
        re.search(f".*({city})$", topic))][0]
    return chosen_topic


def get_emails(sns: client, topic_arn: str):
    """Returns the emails of subscribers subscribed to a city."""
    email_regex = "(.*)[@](.*)(.com|.co.uk|.net|.gov|.org)"
    response = sns.list_subscriptions_by_topic(
        TopicArn=topic_arn
    )
    emails = [r["Endpoint"] for r in response["Subscriptions"]
              if r["SubscriptionArn"] not in ["Deleted", "PendingConfirmation"] and bool(re.search(email_regex, r["Endpoint"]))]
    return emails


def send_email(ses: client, emails: str, html: str):
    """Sends an email using boto3."""
    response = ses.send_email(
        Source=environ["EMAIL"],
        Destination={
            "ToAddresses": emails
        },
        Message={
            "Body": {
                "Html": {
                    "Data": html
                }
            },
            "Subject": {
                "Data": "Starwatch Weekly Report"
            }
        }
    )
    return "DONE"


def clean_city_list(city_list: list):
    """Returns city list with naming conventions of SNS topics."""
    clean_cities = []
    for city in city_list:
        if city == "City of Westminster":
            city = "Westminster"
        else:
            city = city.replace(" ", "-")
            city = city.replace("'", "")
        clean_cities.append(city)
    return clean_cities


def send_all_cities(city_list: list, sns: client, ses: client):
    """Sends an email to all emails subscribed to cities in the database."""
    city_list = clean_city_list(city_list)
    for city in city_list:
        all_topics = list_all_topics(sns)
        topic_list = list_relevant_topics(all_topics)
        topic_arn = retrieve_chosen_topic(topic_list, city)
        emails = get_emails(sns, topic_arn)
        if emails == []:
            print(f"No emails subscribed to {city}")
        else:
            html = write_email(city)
            send_email(ses, emails, html)
            print(f"Email sent for {city}")

    print("Newsletter sent for all subscribers!")


def handler(event, context):
    """Lambda handler"""
    load_dotenv()
    sns = client('sns', aws_access_key_id=environ["AWS_ACCESS_KEY"],
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    ses = client('ses', aws_access_key_id=environ["AWS_ACCESS_KEY"],
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    conn = get_connection()
    city_list = get_all_cities(conn)
    send_all_cities(city_list, sns, ses)


if __name__ == "__main__":
    handler(event="", context="")
