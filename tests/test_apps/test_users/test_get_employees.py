from typing import Any

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.users.serializers import EmployeeSerializer

User = get_user_model()
EMPLOYEE_LIST_URL = 'employee'


def check_json_data(json_data: Any) -> None:
    """Check json data."""
    assert isinstance(json_data, list)
    assert len(json_data) > 0
    employee = json_data[0]
    assert set(employee.keys()) == {
        'id',
        'full_name',
        'tg_username',
        'department_name',
        'survey_count',
        'edited_at',
        'email',
    }


@pytest.mark.django_db
def test_employee_serializer_fields(auth_user: Any, department: Any) -> None:
    """Test serializer fields."""
    auth_user.survey_count = 2
    auth_user.department = department
    serializer = EmployeeSerializer(auth_user)
    serializer_data = serializer.data
    assert set(serializer_data.keys()) == {
        'id',
        'full_name',
        'department_name',
        'email',
        'tg_username',
        'survey_count',
        'edited_at',
    }


@pytest.mark.django_db
def test_employee_list_api_basic(
    auth_client: APIClient, auth_user: Any
) -> None:
    """Test api."""
    url = reverse(EMPLOYEE_LIST_URL)
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data, list)
    assert any(emp['id'] == auth_user.id for emp in response.data)


@pytest.mark.django_db
def test_employee_list_api_sort_name(auth_client: APIClient) -> None:
    """Test sort name."""
    url = reverse(EMPLOYEE_LIST_URL)
    response = auth_client.get(url, {'sort': 'full_name'})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_employee_list_api_sort_edited_at(auth_client: APIClient) -> None:
    """Test sort edited_at."""
    url = reverse(EMPLOYEE_LIST_URL)
    response = auth_client.get(url, {'sort': 'edited_at', 'order': 'desc'})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_employee_list_api_unknown_sort(auth_client: APIClient) -> None:
    """Test unknown sort."""
    url = reverse(EMPLOYEE_LIST_URL)
    response = auth_client.get(url, {'sort': 'unknown'})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_employee_list_view_response_fields(
    auth_user: Any, department: Any, api_client: APIClient
) -> None:
    """Test answer of api."""
    auth_user.survey_count = 2
    auth_user.department = department
    api_client.force_authenticate(user=auth_user)
    url = reverse(EMPLOYEE_LIST_URL)
    response = api_client.get(url)
    assert response.status_code == 200
    json_data = response.json()
    check_json_data(json_data)
