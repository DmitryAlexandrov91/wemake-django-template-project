from http import HTTPStatus

import pytest
from django.conf import settings
from django.test import Client, RequestFactory
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.tokens import AccessToken

from server.apps.users.auth import CookieJWTAuthentication
from server.apps.users.models import CustomUser
from server.apps.users.serializers import CookieTokenObtainPairSerializer
from tests.plugins.users_auth import JWT_COOKIE_ACCESS_NAME, LOGIN_URL
from tests.test_apps.test_users.services import get_user_json


@pytest.mark.django_db
def test_check_access_token_in_cookie(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test existence access token in cokkies."""
    response = client.post(
        LOGIN_URL,
        data=get_user_json(user.email, password),
        timeout=5,
    )
    assert response.status_code == HTTPStatus.OK
    access_cookie = response.cookies[
        settings.JWT_COOKIE[JWT_COOKIE_ACCESS_NAME]
    ]
    access_token = access_cookie.value
    assert int(AccessToken(access_token)['user_id']) == user.id  # type: ignore[arg-type]
    assert access_cookie is not None
    assert response.headers.get(settings.JWT_COOKIE['ACCESS_NAME']) is None


@pytest.mark.django_db
def test_unauthorized_for_bad_credentials(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test that Login view raises 401 for bad user`s credetials."""
    wrong_password = f'{password}_error'
    response = client.post(
        LOGIN_URL,
        data=get_user_json(user.email, wrong_password),
        timeout=5,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_bad_request_for_empty_request_body(
    client: Client, user: CustomUser
) -> None:
    """Test that login view raises 400 for empty request body."""
    response = client.post(LOGIN_URL, data={})
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_cookie_jwt_authentication_invalid_token() -> None:
    """Test wrong access token."""
    request_factory = RequestFactory()
    request = request_factory.post('/some-endpoint')
    request.COOKIES[settings.JWT_COOKIE[JWT_COOKIE_ACCESS_NAME]] = (
        'not.a.valid.jwt.token'
    )
    auth = CookieJWTAuthentication()
    with pytest.raises(exceptions.AuthenticationFailed) as error:
        auth.authenticate(request)
    assert 'Invalid token' in str(error.value)


@pytest.mark.django_db
def test_validate_with_no_user(
    monkeypatch: pytest.MonkeyPatch,
    password: str,
    user: CustomUser,
    client: Client,
) -> None:
    """Test situation for serializer.user = None."""
    serializer = CookieTokenObtainPairSerializer(data={})
    monkeypatch.setattr(
        TokenObtainPairSerializer,
        'validate',
        lambda _serializer, attrs: {'access': 'xxx', 'refresh': 'yyy'},
        raising=True,
    )
    monkeypatch.setattr(serializer, 'user', None, raising=False)
    validated_data = serializer.validate({})
    assert 'access' not in validated_data
    assert 'refresh' not in validated_data
    assert validated_data['id'] is None
    assert validated_data['email'] is None
