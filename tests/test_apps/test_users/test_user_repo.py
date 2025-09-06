from typing import Any

import pytest

from server.apps.users.infra.repository import UserRepo
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.users import UserBatchFactory


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('method_name', 'test_args', 'test_kwargs'),
    [
        ('get_by_pk', [], {'pk': 2}),
        ('get_by_email', [], {'email': 'nontest@example.ru'}),
        ('get_by_tg_id', [], {'tg_id': 9999999999}),
    ],
)
def test_get_methods_raise_exception(
    method_name: str, test_args: list[Any], test_kwargs: dict[str, Any]
) -> None:
    """Test get methods raise DoesNotExist for non-existent objects."""
    repo = resolve(UserRepo)
    method = getattr(repo, method_name)

    with pytest.raises(CustomUser.DoesNotExist):
        method(*test_args, **test_kwargs)


@pytest.mark.django_db
def test_repo_get_by_tg_id(auth_user: CustomUser) -> None:
    """Test UserRepo get_by_tg_id method."""
    assert auth_user.tg_id is not None

    repo = resolve(UserRepo)
    created_user = repo.get_by_tg_id(tg_id=auth_user.tg_id)

    assert isinstance(created_user, CustomUser)
    assert created_user.tg_id == auth_user.tg_id


@pytest.mark.django_db
def test_repo_get_by_email(auth_user: CustomUser) -> None:
    """Test UserRepo get_by_email method."""
    repo = resolve(UserRepo)
    created_user = repo.get_by_email(email=auth_user.email)

    assert isinstance(created_user, CustomUser)
    assert created_user.email == auth_user.email


@pytest.mark.django_db
def test_repo_get_by_pk(auth_user: CustomUser) -> None:
    """Test UserRepo get_by_pk method."""
    repo = resolve(UserRepo)
    created_user = repo.get_by_pk(pk=auth_user.pk)

    assert isinstance(created_user, CustomUser)
    assert created_user == auth_user


@pytest.mark.django_db
def test_repo_get_all(user_batch: UserBatchFactory) -> None:
    """Test UserRepo get_all method."""
    repo = resolve(UserRepo)
    batch_size = 3

    user_batch(batch_size)

    users = repo.get_all()

    assert users.count() == batch_size
    assert all(isinstance(user, CustomUser) for user in users)
