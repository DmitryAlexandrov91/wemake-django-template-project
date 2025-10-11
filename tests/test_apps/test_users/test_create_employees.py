import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.users.models import CustomUser


@pytest.mark.django_db
def test_create_employee_with_existing_email(
    auth_client: APIClient,
    auth_user: CustomUser,
) -> None:
    """Testing invalid employee create with existing email."""
    url = reverse('employee')
    new_user_data = {'full_name': 'New User', 'email': auth_user.email}
    response = auth_client.post(url, data=new_user_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
