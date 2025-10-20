from unittest import mock

import pytest

from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.apps.surveys.tasks import (
    update_one_user_statistics_task,
    update_user_statistics_task,
)
from server.apps.users.models import CustomUser


@pytest.mark.django_db
def test_update_user_statistics_task(
    survey_results_for_user: tuple[CustomUser, int],
) -> None:
    """Test celery task with individual statistics update."""
    user, avg_answer_time = survey_results_for_user
    update_one_user_statistics_task(user_id=user.pk, period=5)
    user_stats = UserStatisticsRepo().get_statistics(user=user)
    assert user_stats.average_answer_sec == avg_answer_time
    assert user_stats.user == user


@pytest.mark.django_db
def test_update_user_statistics_task_empty_qset(
    active_user: CustomUser,
) -> None:
    """Test celery task with individual statistics update and empty qset."""
    update_one_user_statistics_task(user_id=active_user.pk, period=5)
    user_stats = UserStatisticsRepo().get_statistics(user=active_user)
    assert user_stats.average_answer_sec == 0


@pytest.mark.django_db
def test_bulk_update_user_statistics_task(
    mock_celery_tasks: dict[str, mock.Mock],
    mock_statist_service: mock.Mock,
    three_active_users_one_inactive: list[CustomUser],
) -> None:
    """Test bulk statistics update."""
    update_user_statistics_task()
    mock_celery_tasks['group'].assert_called_once()
    mock_celery_tasks['group'].return_value.apply_async.assert_called_once()
