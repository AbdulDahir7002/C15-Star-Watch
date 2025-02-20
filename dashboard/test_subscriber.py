from Subscriber import validate_email, validate_uk_mobile_number, list_all_topics, list_relevant_topics, list_subscribed_topics, retrieve_chosen_topics
import pytest
from boto3 import client
from moto import mock_aws
from unittest.mock import patch, MagicMock
from Subscriber import list_relevant_topics, retrieve_chosen_topics, subscribe_user, unsubscribe_user


@pytest.fixture
def sns():
    with mock_aws():
        yield client("sns", region_name="eu-west-2")


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
    assert retrieve_chosen_topics(topic_list, city_list) == [
        "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-somewhere", "arn:aws:sns:eu-west-2:129033205317:c15-star-watch-city"]


def test_valid_email():
    valid_emails = [
        "test@example.com",
        "user.name+tag@domain.co",
        "user123@subdomain.domain.com",
        "first.last@domain.org"
    ]
    for email in valid_emails:
        assert validate_email(email) is True


def test_invalid_email():
    invalid_emails = [
        "plainaddress",
        "@missingusername.com",
        "missingatdomain.com",
        "user@domain,com",
        "user@domain..com",
        "user@domain.c",
        "user@domain.123"
    ]
    for email in invalid_emails:
        assert validate_email(email) is False


def test_valid_uk_mobile_number():
    valid_numbers = [
        "07123456789",
        "07890123456"
    ]
    for number in valid_numbers:
        assert validate_uk_mobile_number(number) == number


def test_invalid_uk_mobile_number():
    invalid_numbers = [
        ("12345678901", "Please enter a valid phone number starting with 07"),
        ("07123", "Please enter a valid phone number"),
        ("07890123456789", "Please enter a valid phone number"),
        ("0712345678", "Please enter a valid phone number"),
        ("07890123abcd", "Please enter a valid phone number")
    ]
    for number, expected_message in invalid_numbers:
        assert validate_uk_mobile_number(number) == expected_message
