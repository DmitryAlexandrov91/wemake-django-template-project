from typing import Any, final

from django.contrib.auth import hashers
from django.db.models import Count, QuerySet

from server.apps.users.models import CustomUser


@final
class UserRepo:
    """Repository for read User model operations."""

    def get_users_with_department(self) -> QuerySet[CustomUser]:
        """Base queryset with department selection."""
        return CustomUser.objects.select_related('department')

    def get_all(self) -> QuerySet[CustomUser]:
        """Return all User instances from DB."""
        return self.get_users_with_department().all()

    def get_by_pk(self, pk: int) -> CustomUser:
        """Return one User by primary key."""
        return self.get_users_with_department().get(pk=pk)

    def get_by_email(self, email: str) -> CustomUser:
        """Return one User by email."""
        return self.get_users_with_department().get(email=email)

    def get_by_tg_username(self, tg_username: str) -> CustomUser:
        """Return one User by tg_username."""
        return self.get_users_with_department().get(tg_username=tg_username)

    def get_employees_with_survey_count(
        self, order_field: str | None
    ) -> QuerySet[CustomUser]:
        """Get all employees with survey_count."""
        queryset = CustomUser.objects.select_related('department').annotate(
            survey_count=Count('survey_result')
        )
        if order_field:
            queryset.order_by(order_field)
        return queryset

    def get_employee_with_survey_count(self, pk: int) -> CustomUser:
        """Get one employee with survey_count annotation."""
        return (
            CustomUser.objects.select_related('department')
            .annotate(survey_count=Count('survey_result'))
            .get(pk=pk)
        )


@final
class UserRepoSave:
    """Repository for write User model operations."""

    def update_password(self, user: CustomUser, password: str) -> None:
        """Changes user password."""
        user.password = hashers.make_password(password)
        user.save()

    def create_user(self, **kwargs: Any) -> CustomUser:
        """Creates a new user from keyword arguments."""
        department = kwargs.pop('department_name', None)
        return CustomUser.objects.create(**kwargs, department=department)

    def update_user(self, user: CustomUser, **kwargs: Any) -> CustomUser:
        """Update an existing user."""
        department = kwargs.pop('department_name', None)
        CustomUser.objects.filter(pk=user.pk).update(
            **kwargs, department=department
        )
        user.refresh_from_db()
        return user

    def delete(self, pk: int) -> None:
        """Delete an existing user."""
        instance = CustomUser.objects.get(pk=pk)
        instance.delete()
