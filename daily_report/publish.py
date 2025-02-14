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
    return topics


def get_topic(city: str, sns: client):
    """Returns the topic arn of the associated city."""
    topics = [topic["TopicArn"] for topic in sns.list_topics()["Topics"]]
    topic_arn = [name for name in topics if re.search(
        f"(c15-star-watch-{city})", name)]
    return topic_arn


def list_relevant_topics(sns: client) -> list:
    """Returns a list of starwatch topics on AWS."""
    topics = [topic["TopicArn"] for topic in sns.list_topics()["Topics"]]
    starwatch_topics = [name for name in topics if re.search(
        "(c15-star-watch-)(.*)", name)]
    return starwatch_topics


if __name__ == "__main__":
    load_dotenv()
    sns = client("sns", aws_access_key_id=environ["AWS_ACCESS_KEY"],
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    print(list_all_topics(sns))
    print(list_relevant_topics(sns))
    # print(get_topic("testcity", sns))
