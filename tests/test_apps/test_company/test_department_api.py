from http import HTTPStatus
from typing import cast

import pytest
from django.db.models import QuerySet
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.company.views import DepartmentViewSet
from server.apps.users.factories import UserFactory
from server.apps.users.models import CustomUser

DEPARTMENT_NAME = 'department_name'


@pytest.fixture
def api_client() -> APIClient:
    """Provide a DRF APIClient instance for testing."""
    return APIClient()


@pytest.fixture
def auth_client(api_client: APIClient) -> APIClient:
    """Return API client with an authenticated user."""
    user = cast(CustomUser, UserFactory())  # type: ignore[no-untyped-call]
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
def test_create_department(auth_client: APIClient) -> None:
    """Successfully creating a department returns 201 and correct JSON."""
    url = reverse('departments-list')
    payload = {DEPARTMENT_NAME: 'Backend'}

    response = auth_client.post(url, payload, format='json')
    response_data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert DEPARTMENT_NAME in response_data
    assert response_data[DEPARTMENT_NAME] == 'Backend'
    assert 'id' in response_data

    department = Department.objects.get(id=response_data['id'])
    assert department.name == 'Backend'


@pytest.mark.django_db
def test_create_department_without_name(auth_client: APIClient) -> None:
    """Request without department_name returns 400."""
    url = reverse('departments-list')

    response = auth_client.post(url, {}, format='json')
    response_data = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert DEPARTMENT_NAME in response_data


@pytest.mark.django_db
def test_get_queryset_returns_queryset() -> None:
    """Test that get_queryset returns a QuerySet."""
    viewset = DepartmentViewSet()
    queryset = viewset.get_queryset()

    assert isinstance(queryset, QuerySet)
    assert queryset.model is Department


@pytest.mark.django_db
def test_patch_success(department: Department, auth_client: APIClient) -> None:
    """Successfully partial updating a department."""
    url = reverse('departments-detail', kwargs={'pk': department.pk})
    payload = {DEPARTMENT_NAME: 'Test_department_name'}
    response = auth_client.patch(url, payload, format='json')
    response_data = response.json()

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response_data[DEPARTMENT_NAME] != department.name
    assert response_data[DEPARTMENT_NAME] == payload[DEPARTMENT_NAME]
