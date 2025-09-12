from http import HTTPStatus

import pytest
from django.db.models import QuerySet
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.company.views import DepartmentViewSet

DEPARTMENT_NAME = 'department_name'


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
