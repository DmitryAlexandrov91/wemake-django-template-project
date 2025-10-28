import pytest
from celery.result import EagerResult
from django.core.exceptions import ObjectDoesNotExist

from server.apps.company.models import Department
from server.apps.company.tasks import (
    delete_marked_departments_task,
    delete_one_department_task,
)


@pytest.mark.django_db
def test_delete_one_department_task(department: Department) -> None:
    """Test department deletion celery task."""
    department_id = department.id
    task_result: EagerResult = delete_one_department_task.delay(department_id)
    task_result.get(timeout=5)
    assert task_result.state == 'SUCCESS'
    with pytest.raises(ObjectDoesNotExist):
        Department.objects.get(pk=department_id)


@pytest.mark.django_db
def test_delete_marked_departments_task(
    three_departments_to_delete: list[Department],
) -> None:
    """Test bulk departments deletion celery task."""
    department_ids = [
        department.id for department in three_departments_to_delete
    ]
    delete_marked_departments_task.delay()
    for department_id in department_ids:
        with pytest.raises(ObjectDoesNotExist):
            Department.objects.get(pk=department_id)
