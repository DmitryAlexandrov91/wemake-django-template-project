import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.users.models import CustomUser
from tests.plugins.users_requests import RequestMock

FULL_NAME_ATTR = 'full_name'


@pytest.mark.django_db
def test_update_employee(auth_user: CustomUser, auth_client: APIClient) -> None:
    """Testing employee update."""
    url = reverse('employee-update', kwargs={'pk': auth_user.pk})
    payload = {FULL_NAME_ATTR: 'Employee new full name'}
    response = auth_client.patch(url, payload, format='json')

    assert response.status_code == status.HTTP_202_ACCEPTED
    response_data = response.json()

    assert set(response_data.keys()) == {
        'id',
        'full_name',
        'email',
        'tg_username',
        'survey_count',
        'edited_at',
    }

    assert response_data[FULL_NAME_ATTR] != auth_user.full_name
    assert response_data[FULL_NAME_ATTR] == payload[FULL_NAME_ATTR]


@pytest.mark.django_db
def test_update_employee_invalid(
    auth_client: APIClient,
    employee_create_wrong_request: RequestMock,
    auth_user: CustomUser,
) -> None:
    """Testing employee invalid update."""
    url = reverse('employee-update', kwargs={'pk': auth_user.pk})
    response = auth_client.patch(
        url, data=employee_create_wrong_request.data, format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
