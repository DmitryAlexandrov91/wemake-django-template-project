import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.company.models import Department

DEPARTMENT_NAME = 'department_name'
DEPARTMENTS_LIST_URL_NAME = 'departments-list'


@pytest.mark.django_db
def test_empty_department_mark_to_delete(
    department: Department,
    auth_client_user_without_department: APIClient,
) -> None:
    """Test empty department mark to delete."""
    url = reverse('departments-detail', kwargs={'pk': department.pk})
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
    url = reverse('departments-detail', kwargs={'pk': department.pk})
    department_id = department.pk
    auth_client.delete(url)
    deleted_department = Department.objects.get(pk=department_id)
    assert deleted_department.to_delete is False


@pytest.mark.django_db
def test_mark_to_delete_nonexistent_department(
    auth_client: APIClient,
) -> None:
    """Marking nonexistent department as deleted."""
    url = reverse('departments-detail', kwargs={'pk': 999999})
    with pytest.raises(ObjectDoesNotExist):
        auth_client.delete(url)
