"""Script to subscribe users to topics on AWS."""
import re
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


def list_subscribed_topics(email: str, sns: client):
    """Returns a list of subscribed topics."""
    response = sns.list_subscriptions()
    subscriptions = []
    while True:
        subscriptions.extend(response["Subscriptions"])

        if "NextToken" in response:
            response = sns.list_subscriptions(NextToken=response["NextToken"])
        else:
            break

    valid_subscriptions = [
        s["SubscriptionArn"] for s in subscriptions if s["Endpoint"] == email
        and s["SubscriptionArn"] not in ["Deleted", "PendingConfirmation"]]

    return valid_subscriptions


def unsubscribe_user(email: str, sns: client):
    """Unsubscribes user from all topics."""
    subscription_arns = list_subscribed_topics(email, sns)
    if len(subscription_arns) == 0:
        return "Email is not subscribed to any topics!"
    for s in subscription_arns:
        sns.unsubscribe(SubscriptionArn=s)
    return "Unsubscribed!"
