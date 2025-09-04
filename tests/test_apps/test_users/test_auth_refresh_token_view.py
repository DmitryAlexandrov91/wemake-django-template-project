from http import HTTPStatus

import pytest
from django.conf import settings
from django.test import Client

from server.apps.users.models import CustomUser
from tests.plugins.users_auth import (
    JWT_COOKIE_ACCESS_NAME,
    JWT_COOKIE_REFRESH_NAME,
    LOGIN_URL,
    REFRESH_URL,
)
from tests.test_apps.test_users.services import get_user_json


@pytest.mark.django_db
def test_refresh_view_response_body(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test refresh view response body."""
    client.post(
        LOGIN_URL,
        data=get_user_json(user.email, password),
    )
    response = client.post(REFRESH_URL, timeout=5)
    assert response.json() == {'status': 'ok'}


@pytest.mark.django_db
def test_existence_tokens_in_refresh_response(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test that refresh endpount adds access and refresh token in cookie."""
    client.post(
        LOGIN_URL,
        data=get_user_json(user.email, password),
    )
    refresh_response = client.post(REFRESH_URL, timeout=5)
    assert refresh_response.status_code == HTTPStatus.OK
    access_cookie = refresh_response.cookies.get(
        settings.JWT_COOKIE[JWT_COOKIE_ACCESS_NAME],
    )
    refresh_cookie = refresh_response.cookies.get(
        settings.JWT_COOKIE[JWT_COOKIE_REFRESH_NAME],
    )
    assert access_cookie is not None
    assert refresh_cookie is not None
    access_headers_data = refresh_response.headers.get(
        settings.JWT_COOKIE[JWT_COOKIE_ACCESS_NAME],
    )
    refresh_headers_data = refresh_response.headers.get(
        settings.JWT_COOKIE[JWT_COOKIE_REFRESH_NAME],
    )
    assert access_headers_data is None
    assert refresh_headers_data is None


@pytest.mark.django_db
def test_misssing_refresh_token(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test raising of 401 for missing refresh token."""
    client.post(
        LOGIN_URL,
        data=get_user_json(user.email, password),
    )
    client.cookies[settings.JWT_COOKIE[JWT_COOKIE_REFRESH_NAME]] = ''
    response = client.post(REFRESH_URL)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Missing refresh token.' in response.json().get('detail', '')


@pytest.mark.django_db
def test_wrong_refresh_token(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test raising of 401 for wrong refresh token."""
    client.post(
        LOGIN_URL,
        data=get_user_json(user.email, password),
    )
    client.cookies[settings.JWT_COOKIE[JWT_COOKIE_REFRESH_NAME]] = (
        'not.a.valid.jwt.token'
    )
    response = client.post(REFRESH_URL)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Invalid refresh token.' in response.json().get('detail', '')
