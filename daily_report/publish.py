"""Functions to publish messages to our topics in AWS."""

import re
from os import environ
from dotenv import load_dotenv
from boto3 import client


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


def get_topic(city: str, sns: client, all_topics: list):
    """Returns the topic arn of the associated city."""
    topic_arn = [name for name in all_topics if re.search(
        f"(c15-star-watch-{city})", name)]
    return topic_arn[0]


def publish_message(topic_arn: str, sns: client):
    """Publishes a message to specified city."""
    response = sns.publish(TopicArn=topic_arn, Message="</p>WOW</p>",
                           Subject="This is my message to you", MessageStructure="json")
    return response


if __name__ == "__main__":
    load_dotenv()
    sns = client("sns", aws_access_key_id=environ["AWS_ACCESS_KEY"],
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    all_topics = list_all_topics(sns)
    topic_arn = get_topic("testcity", sns, all_topics)
    print(publish_message(topic_arn, sns))
