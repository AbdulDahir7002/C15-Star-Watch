"""Tests for subscribe script."""

import pytest
from boto3 import client
from moto import mock_aws
from unittest.mock import patch, MagicMock
from subscribe import list_relevant_topics, retrieve_chosen_topics, subscribe_user


@pytest.fixture
def sns():
    with mock_aws():
        yield client("sns", region_name="eu-west-2")


@mock_aws
@patch("boto3.client")
def test_list_topics(fake_client):
    mock_sns = MagicMock()
    fake_client.return_value = mock_sns
    mock_sns.list_topics.return_value = {"Topics": [
        {"TopicArn": "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere"},
        {"TopicArn": "arn:aws:sns:eu-west-2:129033205317:West_Africa_Gulf_of_Guinea_0"}
    ]
    }
    assert list_relevant_topics(mock_sns) == [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere"]


def test_retrieve_chosen_topics():
    topic_list = [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhereelse", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-city"]
    city_list = ["city", "somewhere"]
    assert retrieve_chosen_topics(topic_list, city_list) == [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-city"]


@mock_aws
def test_subscribe_user(sns):
    topic_list = []
    for city in ["city1", "city2", "city3", "city4"]:
        topic_name = f"c15-star-watch-{city}"
        topic_arn = sns.create_topic(Name=topic_name)["TopicArn"]
        topic_list.append(topic_arn)

    user_data = {
        "email":
            {
                "address": "fakeemail@gmail.com",
                "cities": ["city1", "city2", "city3"]
            },
        "SMS":
            {
                "number": "+443039403942",
                "cities": ["city1"]
            }

    }

    assert subscribe_user(user_data, topic_list, sns) == "Subscribed!"
