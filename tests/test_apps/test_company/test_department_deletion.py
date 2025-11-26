from collections.abc import Callable

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.surveys.models.surveys import Survey

DEPARTMENT_NAME = 'department_name'
DEPARTMENTS_LIST_URL_NAME = 'departments-list'
DEPARTMENTS_DETAIL_URL_NAME = 'departments-detail'
PK_ATTR = 'pk'


@pytest.mark.django_db
def test_empty_department_mark_to_delete(
    department: Department,
    auth_client_user_without_department: APIClient,
) -> None:
    """Test empty department mark to delete."""
    url = reverse('departments-detail', kwargs={PK_ATTR: department.pk})
    department_id = department.pk
    assert not department.users.exists()
    auth_client_user_without_department.delete(url)
    deleted_department = Department.objects.get(pk=department_id)
    assert deleted_department.to_delete is True


@pytest.mark.django_db
def test_non_empty_department_mark_to_delete(
    department: Department,
    auth_client: APIClient,
) -> None:
    """Test non empty department mark to delete."""
    url = reverse(DEPARTMENTS_DETAIL_URL_NAME, kwargs={PK_ATTR: department.pk})
    department_id = department.pk
    auth_client.delete(url)
    deleted_department = Department.objects.get(pk=department_id)
    assert deleted_department.to_delete is False


@pytest.mark.django_db
def test_mark_to_delete_nonexistent_department(
    auth_client: APIClient,
) -> None:
    """Marking nonexistent department as deleted."""
    url = reverse(DEPARTMENTS_DETAIL_URL_NAME, kwargs={PK_ATTR: 999999})
    with pytest.raises(ObjectDoesNotExist):
        auth_client.delete(url)


@pytest.mark.django_db
def test_department_with_survey_mark_to_delete(
    department: Department,
    create_surveys: Callable[[Department], Survey],
    auth_client_user_without_department: APIClient,
) -> None:
    """Test department with surveys mark to delete."""
    create_surveys(department)
    url = reverse(DEPARTMENTS_DETAIL_URL_NAME, kwargs={PK_ATTR: department.pk})
    department_id = department.pk
    assert not department.users.exists()
    assert department.surveys.exists()
    response = auth_client_user_without_department.delete(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    deleted_department = Department.objects.get(pk=department_id)
    assert deleted_department.to_delete is False
