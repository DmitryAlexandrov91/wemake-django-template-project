from typing import final

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
