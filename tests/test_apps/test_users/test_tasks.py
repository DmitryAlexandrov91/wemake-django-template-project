import pytest
from celery.result import EagerResult

from server.apps.users.models import CustomUser
from server.apps.users.tasks import (
    inactivate_marked_users_task,
    inactivate_single_user_task,
)


@pytest.mark.django_db
def test_inactivate_single_user_task(active_user: CustomUser) -> None:
    """Test user deactivation celery task."""
    user_id = active_user.id
    task_result: EagerResult = inactivate_single_user_task.delay(user_id)
    task_result.get(timeout=5)
    assert task_result.state == 'SUCCESS'
    updated_user = CustomUser.objects.get(pk=user_id)
    assert updated_user.is_active is False


@pytest.mark.django_db
def test_inactivate_marked_users_task(
    three_users_to_inactivate: list[CustomUser],
) -> None:
    """Test bulk user inactivation."""
    user_ids = [user.id for user in three_users_to_inactivate]
    inactivate_marked_users_task.delay()
    for user_id in user_ids:
        updated_user = CustomUser.objects.get(pk=user_id)
        assert updated_user.is_active is False
