"""Tests for subscribe script."""

import pytest
import os
from email.mime.image import MIMEImage
from boto3 import client
from moto import mock_aws
from unittest.mock import patch, MagicMock
from send_email import list_relevant_topics, retrieve_chosen_topic, clean_city_list


@pytest.fixture
def sns():
    with mock_aws():
        yield client("sns", region_name="eu-west-2")


@pytest.fixture
def ses():
    with mock_aws():
        yield client("ses", region_name="eu-west-2")


@pytest.fixture
def subscribed_topics(sns):
    topic_list = []
    for city in ["city1", "city2", "city3", "city4"]:
        topic_name = f"c15-star-watch-{city}"
        topic_arn = sns.create_topic(Name=topic_name)["TopicArn"]
        topic_list.append(topic_arn)
    return topic_list


@pytest.fixture
def user_data():
    data = {
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
    return data


def test_list_topics():
    all_topics = ["arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere",
                  "arn:aws:sns:eu-west-2:129033205317:West_Africa_Gulf_of_Guinea_0"]
    assert list_relevant_topics(all_topics) == [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere"]


def test_retrieve_chosen_topics():
    topic_list = [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhereelse", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-city"]
    city_list = ["city", "somewhere"]
    assert retrieve_chosen_topic(
        topic_list, city_list) == "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere"


def test_list_relevant_topics():
    topic_list = [
        "arn:aws:sns:eu-west-2:129033205317:c15-sdoicjotar-watch-somewhere", "arn:aws:sns:eu-west-2:129033205317:c15-ssjodijtar-watch-somewhereelse", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-city"]
    assert list_relevant_topics(topic_list) == [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-city"]


@pytest.mark.parametrize("inp, exp", [(["City of Westminster"], ["Westminster"]), (["St David's"], ["St-Davids"]), (["This is a city"], ["This-is-a-city"]), (["City of Westminster", "St Davids", "Aberdeen"], ["Westminster", "St-Davids", "Aberdeen"])])
def test_clean_cities(inp, exp):
    assert clean_city_list(inp) == exp
