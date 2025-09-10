from typing import final

from django.contrib.auth import hashers
from django.db.models import QuerySet

from server.apps.users.models import CustomUser


@final
class UserRepo:
    """Repository for User model operations."""

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

    def get_by_tg_id(self, tg_id: int) -> CustomUser:
        """Return one User by tg_id."""
        return self.get_users_with_department().get(tg_id=tg_id)

    def update_password(self, user: CustomUser, password: str) -> None:
        """Changes user password."""
        user.password = hashers.make_password(password)
        user.save()
