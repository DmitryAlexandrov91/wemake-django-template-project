from typing import Any

import pytest
from django.core.exceptions import ValidationError

from server.apps.users.validators import (
    validate_request,
    validate_telegram_username,
)


@pytest.mark.django_db
def test_valid_request(valid_request: Any) -> None:
    """Tests validation of a valid request."""
    assert validate_request(valid_request) == valid_request.data['email']


@pytest.mark.django_db
def test_wrong_request(wrong_request: Any) -> None:
    """Tests a request with invalid email."""
    assert validate_request(wrong_request) is None


@pytest.mark.django_db
def test_empty_request(empty_request: Any) -> None:
    """Tests an empty email request."""
    assert validate_request(empty_request) is None


@pytest.mark.parametrize(
    'username',
    [
        '@user',
        '@user123',
        '@user_',
        '@A_bC_123',
        '@abc_1',
    ],
)
def test_valid_usernames(username: Any) -> None:
    """Tests Telegram username."""
    validate_telegram_username(username)


@pytest.mark.parametrize(
    'username',
    [
        123,
        None,
        ['@nick'],
    ],
)
def test_invalid_type(username: Any) -> None:
    """Tests Telegram username."""
    with pytest.raises(ValidationError):
        validate_telegram_username(username)


@pytest.mark.parametrize(
    'username',
    [
        'user',
        '@',
        '@user!',
        '@юзер',
        '@user name',
        '@user-name',
        '@user.name',
        '@ ',
        '@user$',
        '@_user',
    ],
)
def test_invalid_usernames(username: Any) -> None:
    """Tests Telegram username."""
    with pytest.raises(ValidationError):
        validate_telegram_username(username)
