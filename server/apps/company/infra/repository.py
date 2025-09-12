from typing import Any, final

from django.db.models import QuerySet

from server.apps.company.models import Department


@final
class DepartmentRepo:
    """Repository for accessing Department objects from the database."""

    def get_all(self) -> QuerySet[Department]:
        """A method for extracting all department objects from the database."""
        return Department.objects.all().select_related('head')

    def get_by_pk(self, pk: int) -> Department:
        """A method for retrieving a Department object by its primary key."""
        return Department.objects.select_related('head').get(pk=pk)

    def update_department(
        self, department: Department, **kwargs: Any
    ) -> Department:
        """Update an existing department."""
        Department.objects.filter(pk=department.pk).update(**kwargs)
        department.refresh_from_db()
        return department
