import pytest

from server.apps.users.infra.repository import UserRepoSave
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.department_factory import DepartmentFactory


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


@pytest.mark.django_db
def test_get_all_to_inactivate_ids(
    three_users_to_inactivate: list[CustomUser],
) -> None:
    """Test getting user ids to inactivate."""
    repo = UserRepoSave()
    expected_ids = [user.id for user in three_users_to_inactivate]
    res = repo.get_all_to_inactivate_ids()
    assert set(res) == set(expected_ids)
    for user_id in res:
        user = CustomUser.objects.get(pk=user_id)
        assert user.is_active is True
        assert user.to_inactivate is True


@pytest.mark.django_db
def test_mark_inactive(active_user: CustomUser) -> None:
    """Test user unactivation."""
    assert active_user.is_active is True
    repo = UserRepoSave()
    repo.mark_inactive(active_user.pk)
    updated_user = CustomUser.objects.get(pk=active_user.pk)
    assert updated_user.is_active is False


@pytest.mark.django_db
def test_update_user(
    auth_user: CustomUser, department_factory: DepartmentFactory
) -> None:
    """Test update user with department."""
    new_department = department_factory()
    user_data = {
        'email': 'another@email.com',
        'full_name': auth_user.full_name,
        'position': auth_user.position,
        'role': auth_user.role,
        'is_staff': auth_user.is_staff,
        'department_name': new_department,
    }

    resolve(UserRepoSave).update_user(auth_user, **user_data)
    assert auth_user.department == new_department
