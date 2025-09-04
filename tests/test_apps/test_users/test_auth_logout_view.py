from http import HTTPStatus

import pytest
from django.conf import settings
from django.test import Client

from server.apps.users.models import CustomUser
from tests.plugins.users_auth import (
    JWT_COOKIE_ACCESS_NAME,
    JWT_COOKIE_REFRESH_NAME,
    LOGIN_URL,
    LOGOUT_URL,
)
from tests.test_apps.test_users.services import get_user_json


@pytest.mark.django_db
def test_logout_response(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test for Logout view."""
    client.post(
        LOGIN_URL,
        data=get_user_json(user.email, password),
    )
    response = client.post(LOGOUT_URL)
    assert response.status_code == HTTPStatus.OK
    access_cookie = response.cookies.get(
        settings.JWT_COOKIE[JWT_COOKIE_ACCESS_NAME]
    )
    access_token = access_cookie.value if access_cookie else None
    refresh_cookie = response.cookies.get(
        settings.JWT_COOKIE[JWT_COOKIE_REFRESH_NAME]
    )
    refresh_token = refresh_cookie.value if refresh_cookie else None
    assert not access_token
    assert not refresh_token
