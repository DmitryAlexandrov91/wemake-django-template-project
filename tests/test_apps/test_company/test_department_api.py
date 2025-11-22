from http import HTTPStatus

import pytest
from django.db.models import QuerySet
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.company.views import DepartmentViewSet
from server.apps.users.models import CustomUser
from tests.plugins.auth_client_factory import AuthClientFactory
from tests.plugins.department_factory import DepartmentBatchFactory

DEPARTMENT_NAME = 'department_name'
DEPARTMENTS_LIST_URL_NAME = 'departments-list'


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
    url = reverse(DEPARTMENTS_LIST_URL_NAME)

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


@pytest.mark.django_db
def test_get_list_department(
    auth_client_factory: AuthClientFactory,
    active_user: CustomUser,
    department_batch: DepartmentBatchFactory,
) -> None:
    """Get department list."""
    batch_size = 3
    department_batch(batch_size)
    url = reverse(DEPARTMENTS_LIST_URL_NAME)
    auth_client = auth_client_factory(active_user)
    response = auth_client.get(url)
    response = auth_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert len(response.data['data']) == batch_size


@pytest.mark.django_db
def test_get_list_department_ordered(
    auth_client_factory: AuthClientFactory,
    active_user: CustomUser,
    department_batch: DepartmentBatchFactory,
) -> None:
    """Check departments are sorted by name ascending."""
    batch_size = 3
    department_batch(batch_size)
    url = reverse(DEPARTMENTS_LIST_URL_NAME)
    auth_client = auth_client_factory(active_user)
    response = auth_client.get(url)

    assert [dep['department_name'] for dep in response.data['data']] == [
        f'Dep{dep_number}' for dep_number in range(batch_size)
    ]


@pytest.mark.django_db
def test_get_list_all_department(
    auth_client_factory: AuthClientFactory,
    active_user: CustomUser,
    department_batch: DepartmentBatchFactory,
) -> None:
    """Get all department list."""
    batch_size = 3
    department_batch(batch_size)
    url = reverse(DEPARTMENTS_LIST_URL_NAME)
    auth_client = auth_client_factory(active_user)
    response = auth_client.get(url, {'per_page': 'all'})
    assert response.status_code == HTTPStatus.OK
    assert len(response.data) == batch_size
