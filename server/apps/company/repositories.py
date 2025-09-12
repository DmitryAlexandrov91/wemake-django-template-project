from typing import Any

from django.db.models import QuerySet

from server.apps.company.models import Department


class DepartmentRepository:
    """Repository for Department model."""

    @classmethod
    def create(cls, **kwargs: Any) -> Department:
        """Create and return a new Department instance."""
        return Department.objects.create(**kwargs)

    @classmethod
    def all_with_related(cls) -> QuerySet[Department]:
        """Return all departments with related FK (e.g. employees)."""
        return Department.objects.select_related('some_fk_field').all()
