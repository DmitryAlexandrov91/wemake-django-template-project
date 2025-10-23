import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.users.models import CustomUser

EMPLOYEE_URL = reverse('employee')


@pytest.mark.django_db
def test_delete_employee(
    active_user: CustomUser,
    auth_client: APIClient,
) -> None:
    """Test deleting an employee by primary key."""
    response = auth_client.delete(f'{EMPLOYEE_URL}/{active_user.id}')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_not_found_user(auth_client: APIClient) -> None:
    """Test that deleting a nonexistent employee returns 404."""
    employee_count = CustomUser.objects.count() + 1
    response = auth_client.delete(f'{EMPLOYEE_URL}/{employee_count}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
