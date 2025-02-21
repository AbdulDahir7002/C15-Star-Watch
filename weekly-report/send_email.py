"""Function to send an email using boto3."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import re
from os import environ
from dotenv import load_dotenv
from boto3 import client


from weekly_report_generator import write_email, get_all_cities, get_connection


def list_all_topics(sns: client):
    """Returns a list of all topics on AWS."""
    response = sns.list_topics()
    topics = []

    while "NextToken" in response:
        topics.extend(response["Topics"])
        response = sns.list_topics(NextToken=response["NextToken"])
    topics.extend(response["Topics"])
    return [topic["TopicArn"] for topic in topics]


def list_relevant_topics(all_topics: list) -> list:
    """Returns a list of starwatch topics on AWS."""
    starwatch_topics = [name for name in all_topics if re.search(
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


def send_email(ses: client, emails: list, html: str):
    """Sends an email using boto3."""

    msg = MIMEMultipart('related')
    msg.attach(MIMEText(html, 'html'))
    msg['From'] = environ["EMAIL"]
    msg['To'] = ', '.join(emails)
    msg['Subject'] = "Starwatch Weekly Report"

    with open("average_coverage_graph.png", 'rb') as img:
        img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header("Content-ID", '<image1>')
        image.add_header("Content-Disposition", 'inline',
                         filename="average_coverage_graph.png")
        msg.attach(image)

    with open("average_visibility_graph.png", 'rb') as img:
        img_data = img.read()
        image = MIMEImage(img_data)
        image.add_header("Content-ID", '<image2>')
        image.add_header("Content-Disposition", 'inline',
                         filename="average_visibility_graph.png")
        msg.attach(image)

    ses.send_raw_email(
        Source=environ["EMAIL"],
        Destinations=emails,
        RawMessage={
            "Data": msg.as_string()
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
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"], region_name=environ["REGION"])
    ses = client('ses', aws_access_key_id=environ["AWS_ACCESS_KEY"],
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"], region_name=environ["REGION"])
    conn = get_connection()
    city_list = get_all_cities(conn)
    send_all_cities(city_list, sns, ses)


if __name__ == "__main__":
    handler("", "")
