from typing import Any, final

from django.contrib.auth import hashers
from django.db.models import Count, QuerySet
from django.db.models.functions import Lower

from server.apps.users.models import CustomUser

DEPARTMENT = 'department'


@final
class UserRepo:
    """Repository for read User model operations."""

    def get_users_with_department(self) -> QuerySet[CustomUser]:
        """Base queryset with department selection."""
        return CustomUser.objects.filter(is_active=True).select_related(
            'department', 'statistics'
        )

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
        self, sort_field: str | None, order_param: str
    ) -> QuerySet[CustomUser]:
        """Get all employees with survey_count."""
        queryset = (
            CustomUser.objects.filter(is_active=True)
            .select_related(DEPARTMENT)
            .prefetch_related('statistics')
            .annotate(survey_count=Count('survey_result'))
        )
        if sort_field == 'full_name':
            queryset = (
                queryset.order_by(Lower(sort_field))
                if order_param == 'asc'
                else queryset.order_by(Lower(sort_field).desc())
            )
        elif sort_field == 'edited_at':
            queryset = (
                queryset.order_by(sort_field)
                if order_param == 'asc'
                else queryset.order_by(f'-{sort_field}')
            )
        return queryset

    def get_employee_with_survey_count(self, pk: int) -> CustomUser:
        """Get one employee with survey_count annotation."""
        return (
            CustomUser.objects.filter(is_active=True)
            .select_related(DEPARTMENT)
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
        if department is not None:
            kwargs[DEPARTMENT] = department
        CustomUser.objects.filter(pk=user.pk).update(**kwargs)
        user.refresh_from_db()
        return user

    def mark_to_inactivate(self, pk: int) -> None:
        """Prepare user for a delayed inactivation."""
        user = CustomUser.objects.get(pk=pk)
        user.to_inactivate = True
        user.save()

    def get_all_to_inactivate_ids(self) -> list[int]:
        """Returns all users for inactivation."""
        return list(
            CustomUser.objects.filter(
                is_active=True,
                to_inactivate=True,
            ).values_list('id', flat=True)
        )

    def mark_inactive(self, pk: int) -> None:
        """Inactivate single user."""
        user = CustomUser.objects.get(pk=pk)
        user.is_active = False
        user.save()

    def get_active_user_ids(self) -> QuerySet[CustomUser, int]:
        """Gets active user id's only."""
        return CustomUser.objects.filter(is_active=True).values_list(
            'id', flat=True
        )
