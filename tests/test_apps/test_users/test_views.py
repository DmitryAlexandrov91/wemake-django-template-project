from typing import Any

import pytest
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.users.models import CustomUser
from tests.plugins.users_requests import RequestMock

PASS_RECOVERY_URL = reverse('password-recovery')
EMPLOYEE_URL = reverse('employee')


@pytest.mark.django_db
def test_post_success(
    mocked_send_password_recovery_email: Any,
    api_client: APIClient,
    active_user: CustomUser,
    valid_request: Any,
) -> None:
    """Testing successful password recovery."""
    response = api_client.post(PASS_RECOVERY_URL, valid_request.data)
    assert response.status_code == status.HTTP_200_OK
    mocked_send_password_recovery_email.assert_called_once()
    old_password = active_user.password
    active_user.refresh_from_db()
    assert not check_password(old_password, active_user.password)


def test_invalid_email_format(
    api_client: APIClient, wrong_request: RequestMock
) -> None:
    """Testing view with invalid-email."""
    with pytest.raises(ValidationError):
        api_client.post(PASS_RECOVERY_URL, wrong_request.data)


@pytest.mark.django_db
def test_valid_email_no_user(
    api_client: APIClient, valid_request: RequestMock
) -> None:
    """Testing view with email but no such user."""
    response = api_client.post(PASS_RECOVERY_URL, valid_request.data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_no_email_in_request(
    api_client: APIClient, empty_request: RequestMock
) -> None:
    """Testing view with empty email."""
    with pytest.raises(ValidationError):
        api_client.post(PASS_RECOVERY_URL, empty_request.data)


@pytest.mark.django_db
def test_create_employee_success(
    auth_client: APIClient,
    employee_create_request: RequestMock,
    department: Department,
) -> None:
    """Testing new employee creation."""
    CustomUser.objects.all().delete()
    employee_create_request.data['department_name'] = department.name
    response = auth_client.post(EMPLOYEE_URL, data=employee_create_request.data)
    assert response.status_code == status.HTTP_201_CREATED
    created_user = CustomUser.objects.get(
        email=employee_create_request.data['email']
    )
    assert created_user.role == 'employee'
    assert created_user.is_staff is False
    assert created_user.department == department
    assert created_user.edited_at is not None


@pytest.mark.django_db
def test_create_employee_invalid(
    auth_client: APIClient, employee_create_wrong_request: RequestMock
) -> None:
    """Testing new employee creation."""
    response = auth_client.post(
        EMPLOYEE_URL, data=employee_create_wrong_request.data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
