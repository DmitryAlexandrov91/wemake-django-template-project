from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypedDict, Unpack

import pytest

from server.apps.users.models import CustomUser

if TYPE_CHECKING:
    from tests.plugins.fakery import FakeryM

type UserFactory = Callable[[Unpack[_UserFactoryParams]], CustomUser]

type UserBatchFactory = Callable[[int], list[CustomUser]]


class _UserFactoryParams(TypedDict, total=False):
    """Base params for UserFactory."""

    username: str
    email: str
    first_name: str
    last_name: str
    patronymic: str
    position: str
    role: str
    is_active: bool
    is_staff: bool
    tg_id: int


@pytest.fixture
def user_factory(fakery_m: FakeryM[CustomUser]) -> UserFactory:
    """Factory fixture for creating User instances."""

    def factory(**kwargs: Unpack[_UserFactoryParams]) -> CustomUser:
        return fakery_m(CustomUser)(**kwargs)

    return factory


@pytest.fixture
def user_batch(
    user_factory: UserFactory,
) -> UserBatchFactory:
    """Return a factory that creates `batch_size` User instances."""

    def factory(batch_size: int) -> list[CustomUser]:
        return [
            user_factory(
                username=f'user{user_number}',
                email=f'user{user_number}@example.ru',
            )
            for user_number in range(batch_size)
        ]

    return factory


@pytest.fixture
def auth_user(user_factory: UserFactory) -> CustomUser:
    """Fixture that create a single User instance."""
    return user_factory(
        username='testuser',
        email='test@example.com',
        first_name='Test first_name',
        last_name='Test last_name',
        patronymic='Test patronymic',
        position='Test position',
        role='User',
        is_active=True,
        is_staff=False,
        tg_id=1234567890,
    )
