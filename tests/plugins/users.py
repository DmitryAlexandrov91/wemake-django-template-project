from __future__ import annotations

import secrets
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypedDict, Unpack

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from pytest_mock import MockFixture

from server.apps.users import admin, models
from server.common.constants import DATA_LENGHT
from tests.plugins.users_requests import RequestMock

if TYPE_CHECKING:
    from tests.plugins.fakery import FakeryM

type UserFactory = Callable[[Unpack[_UserFactoryParams]], models.CustomUser]

type UserBatchFactory = Callable[[int], list[models.CustomUser]]


class _UserFactoryParams(TypedDict, total=False):
    """Base params for UserFactory."""

    username: str
    email: str
    full_name: str
    position: str
    role: str
    is_active: bool
    is_staff: bool
    tg_username: str
    department: Any
    survey_count: int
    edited_at: str
    to_inactivate: bool


@pytest.fixture
def user_factory(fakery_m: FakeryM[models.CustomUser]) -> UserFactory:
    """Factory fixture for creating User instances."""

    def factory(**kwargs: Unpack[_UserFactoryParams]) -> models.CustomUser:
        return fakery_m(models.CustomUser)(**kwargs)

    return factory


@pytest.fixture
def user_batch(
    user_factory: UserFactory,
) -> UserBatchFactory:
    """Return a factory that creates `batch_size` User instances."""

    def factory(batch_size: int, **kwargs: Any) -> list[models.CustomUser]:
        return [
            user_factory(
                username=f'user{user_number}',  # noqa: WPS226
                email=f'user{user_number}@example.ru',
            )
            for user_number in range(batch_size)
        ]

    return factory


@pytest.fixture
def auth_user(user_factory: UserFactory, department: Any) -> models.CustomUser:
    """Fixture that create a single User instance."""
    return user_factory(
        username='testuser',
        email='test@example.com',
        full_name='Test name',
        position='Test position',
        role='User',
        is_active=True,
        is_staff=False,
        tg_username='@1234567890',
        department=department,
        survey_count=1,
        edited_at='25.02.2025',
    )


@pytest.fixture
def mocked_send_mail(mocker: MockFixture) -> Any:
    """Mock the email sending task."""
    return mocker.patch(
        'server.apps.users.tasks.send_recovery_email_task.delay',
        return_value=None,
    )


@pytest.fixture
def active_user(
    valid_request: RequestMock, fakery_m: FakeryM[models.CustomUser]
) -> models.CustomUser:
    """Fixture for creating an active user."""
    original_password = secrets.token_urlsafe(DATA_LENGHT)
    return fakery_m(models.CustomUser)(
        email=valid_request.data['email'],
        password=original_password,
        is_active=True,
    )


@pytest.fixture
def admin_user(db) -> Any:  # type: ignore[no-untyped-def]
    """Fixture for admin user."""
    user = get_user_model()
    return user.objects.create_superuser('admin', 'password')


@pytest.fixture
def three_users_to_inactivate(
    user_factory: UserFactory,
) -> list[models.CustomUser]:
    """Fixture that creates three users with to_inactivate=True."""
    return [
        user_factory(
            username=f'user{user_number}',
            email=f'user{user_number}@example.ru',  # noqa: WPS226
            to_inactivate=True,
        )
        for user_number in range(3)
    ]


@pytest.fixture
def user_admin() -> admin.CustomUserAdmin:
    """UserAdmin fixture."""
    return admin.CustomUserAdmin(models.CustomUser, AdminSite())
