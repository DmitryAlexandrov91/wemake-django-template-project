from typing import Any

import pytest

from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.users import UserBatchFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('method_name', 'test_args', 'test_kwargs'),
    [
        ('get_by_pk', [], {'pk': 2}),
        ('get_by_email', [], {'email': 'nontest@example.ru'}),
        ('get_by_tg_username', [], {'tg_username': '@default_username'}),
    ],
)
def test_get_methods_raise_exception(
    method_name: str, test_args: list[Any], test_kwargs: dict[str, Any]
) -> None:
    """Test get methods raise DoesNotExist for non-existent objects."""
    method = getattr(resolve(UserRepo), method_name)

    with pytest.raises(CustomUser.DoesNotExist):
        method(*test_args, **test_kwargs)


@pytest.mark.django_db
def test_repo_get_by_tg_id(auth_user: CustomUser) -> None:
    """Test UserRepo get_by_tg_username method."""
    assert auth_user.tg_username is not None

    created_user = resolve(UserRepo).get_by_tg_username(
        tg_username=auth_user.tg_username
    )

    assert isinstance(created_user, CustomUser)
    assert created_user.tg_username == auth_user.tg_username


@pytest.mark.django_db
def test_repo_get_by_email(auth_user: CustomUser) -> None:
    """Test UserRepo get_by_email method."""
    created_user = resolve(UserRepo).get_by_email(email=auth_user.email)

    assert isinstance(created_user, CustomUser)
    assert created_user.email == auth_user.email


@pytest.mark.django_db
def test_repo_get_by_pk(auth_user: CustomUser) -> None:
    """Test UserRepo get_by_pk method."""
    created_user = resolve(UserRepo).get_by_pk(pk=auth_user.pk)

    assert isinstance(created_user, CustomUser)
    assert created_user == auth_user


@pytest.mark.django_db
def test_repo_get_all(user_batch: UserBatchFactory) -> None:
    """Test UserRepo get_all method."""
    batch_size = 3
    user_batch(batch_size)
    users = resolve(UserRepo).get_all()

    assert users.count() == batch_size
    assert all(isinstance(user, CustomUser) for user in users)


@pytest.mark.django_db
def test_create_user(auth_user: CustomUser) -> None:
    """Test UserRepo user creation."""
    user_data = {
        'email': 'another@email.com',
        'full_name': auth_user.full_name,
        'position': auth_user.position,
        'role': auth_user.role,
        'is_staff': auth_user.is_staff,
    }
    created_user = resolve(UserRepoSave).create_user(**user_data)

    assert isinstance(created_user, CustomUser)
    assert CustomUser.objects.filter(pk=created_user.pk).exists()
    assert created_user.full_name == user_data['full_name']
