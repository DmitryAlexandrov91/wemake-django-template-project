from typing import Any

import pytest
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.users.models import CustomUser

url = reverse('password-recovery')
json = 'json'


@pytest.mark.django_db
def test_post_success(
    mocked_send_mail: Any,
    api_client: APIClient,
    active_user: CustomUser,
    valid_request: Any,
) -> None:
    """Testing successful password recovery."""
    response = api_client.post(url, valid_request.data)
    assert response.status_code == status.HTTP_200_OK
    mocked_send_mail.assert_called_once()
    old_password = active_user.password
    active_user.refresh_from_db()
    assert not check_password(old_password, active_user.password)


def test_invalid_email_format(
    api_client: APIClient, wrong_request: Any
) -> None:
    """Testing view with invalid-email."""
    with pytest.raises(ValidationError):
        api_client.post(url, wrong_request.data)


@pytest.mark.django_db
def test_valid_email_no_user(api_client: APIClient, valid_request: Any) -> None:
    """Testing view with email but no such user."""
    response = api_client.post(url, valid_request.data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_no_email_in_request(api_client: APIClient, empty_request: Any) -> None:
    """Testing view with empty email."""
    with pytest.raises(ValidationError):
        api_client.post(url, empty_request.data)
