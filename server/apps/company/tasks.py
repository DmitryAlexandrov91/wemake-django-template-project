from collections.abc import Callable

from celery import group, shared_task

from server.apps.company.infra.repository import DepartmentRepo
from server.di import resolve

TaskFunction = Callable[[str, str], bool]


@shared_task  # type: ignore[misc]
def delete_one_department_task(department_id: int) -> None:
    """Celery task for deletion of one department."""
    resolve(DepartmentRepo).delete(pk=department_id)


@shared_task  # type: ignore[misc]
def delete_marked_departments_task() -> None:
    """Celery task for deletion of all marked departments."""
    department_ids = resolve(DepartmentRepo).get_all_to_delete_ids()
    update_group = group(
        delete_one_department_task.s(department_id=department_id)
        for department_id in department_ids
    )
    update_group.apply_async()
