"""Script to subscribe users to topics on AWS."""
import re
from os import environ
from dotenv import load_dotenv
from boto3 import client


def list_relevant_topics(sns: client) -> list:
    """Returns a list of starwatch topics on AWS."""
    topics = [topic["TopicArn"] for topic in sns.list_topics()["Topics"]]
    starwatch_topics = [name for name in topics if re.search(
        "(c15-star-watch-)(.*)", name)]
    return starwatch_topics


def retrieve_chosen_topics(topic_list: list, city_list: list) -> list:
    """Returns a list of topics the user has chosen to subscribe to."""
    chosen_topics = [topic for topic in topic_list for city in city_list if bool(
        re.search(f".*({city})$", topic))]
    return chosen_topics


def subscribe_user(user_data: dict, topic_list: list, sns: client):
    """Subscribes a user to chosen topic(s)."""
    email_topics = retrieve_chosen_topics(
        topic_list, user_data["email"]["cities"])
    sms_topics = retrieve_chosen_topics(
        topic_list, user_data["SMS"]["cities"])

    for topic in email_topics:
        response = sns.subscribe(
            TopicArn=topic,
            Protocol="email",
            Endpoint=user_data["email"]["address"],
            ReturnSubscriptionArn=True
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return f"Could not subscribe user to {topic}."

    for topic in sms_topics:
        sns.subscribe(
            TopicArn=topic,
            Protocol="sms",
            Endpoint=user_data["SMS"]["number"],
            ReturnSubscriptionArn=True
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return f"Could not subscribe user to {topic}."
    return "Subscribed!"


def list_subscribed_topics(email: str):
    """Returns a list of subscribed topics."""
    response = sns.list_subscriptions()
    subscriptions = sns.list_subscriptions()["Subscriptions"]
    while "NextToken" in response:
        subscriptions.extend(response["Subscriptions"])
        response = sns.list_subscriptions()["NextToken"]
    valid_subscriptions = [
        s for s in subscriptions if s["Endpoint"] == email]
    return subscriptions


def unsubscribe_user(user_data: dict):
    """Unsubscribes user from all topics."""
    pass


if __name__ == "__main__":
    load_dotenv()
    sns = client('sns', aws_access_key_id=environ["AWS_ACCESS_KEY"],
                 aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    # print([subscription["Endpoint"]
    #       for subscription in sns.list_subscriptions()["Subscriptions"]])
    print(list_subscribed_topics("beenzu13@yahoo.com"))
