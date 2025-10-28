from typing import Any, final

from django.db.models import Count, QuerySet

from server.apps.company.models import Department


@final
class DepartmentRepo:
    """Repository for Department model."""

    def get_all(self) -> QuerySet[Department]:
        """A method for extracting all department objects from the database."""
        return (
            Department.objects.all()
            .select_related('head')
            .prefetch_related('users')
        )

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

    def get_all_ordered_by_name(self) -> QuerySet[Department]:
        """Return all departments ordered by name ASC."""
        return (
            self.get_all()
            .annotate(employees_count=Count('users'))
            .order_by('name')
        )

    def create(self, **kwargs: Any) -> Department:
        """Create and return a new Department instance."""
        return Department.objects.create(**kwargs)

    def get_all_to_delete_ids(self) -> list[int]:
        """Return department ids marked for deletion."""
        return list(
            Department.objects.filter(to_delete=True).values_list(
                'id', flat=True
            )
        )

    def delete(self, pk: int) -> None:
        """Delete one department."""
        department = Department.objects.get(pk=pk)
        department.delete()
