"""Tests for nasa apod api requests"""

import pytest
from nasa_apod import get_picture_of_day, check_media_type, check_title, check_url, check_valid_apod


@pytest.mark.parametrize("test_input, expected", [("https://example.com", True), ("www.shouldntwork.com", False)])
def test_check_url_valid_input(test_input, expected):
    assert check_url(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [("we8fhawe[ofah]", False), (2233, False)])
def test_check_url_invalid_input(test_input, expected):
    assert check_url(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [("we8fhawe[ofah]", True), ("title_name", True)])
def test_check_title_valid_input(test_input, expected):
    assert check_title(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [({"title"}, False), (2233, False)])
def test_check_title_invalid_input(test_input, expected):
    assert check_title(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [("Image", True), ("image", True), ("Video", True), ("video", True), ("definitelyfalse", False)])
def test_check_media_type_valid_input(test_input, expected):
    assert check_media_type(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [(30230, False), ({"Image": 39}, False)])
def test_check_media_type_invalid_input(test_input, expected):
    assert check_media_type(test_input) == expected


@pytest.mark.parametrize("test_input, expected", [({"media_type": "image", "title": "sometitle", "url": "https://example.com"}, True), ({"media_type": 909, "title": 843, "url": "httiips://example.com"}, False)])
def test_check_all_valid_input(test_input, expected):
    assert check_valid_apod(test_input) == expected
