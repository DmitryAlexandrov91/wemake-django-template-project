from unittest import mock

import pytest
from celery.result import EagerResult
from django.core.exceptions import ObjectDoesNotExist

from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.apps.surveys.models import Question, Survey
from server.apps.surveys.tasks import (
    delete_marked_questions_task,
    delete_marked_surveys_task,
    delete_one_question_task,
    delete_one_survey_task,
    update_one_user_statistics_task,
    update_user_statistics_task,
)
from server.apps.users.models import CustomUser
from server.di import resolve


@pytest.mark.django_db
def test_update_user_statistics_task(
    survey_results_for_user: tuple[CustomUser, int],
) -> None:
    """Test celery task with individual statistics update."""
    user, avg_answer_time = survey_results_for_user
    update_one_user_statistics_task(user_id=user.pk, period=5)
    user_stats = resolve(UserStatisticsRepo).get_statistics(user=user)
    assert user_stats.average_answer_sec == avg_answer_time
    assert user_stats.user == user


@pytest.mark.django_db
def test_update_user_statistics_task_empty_qset(
    active_user: CustomUser,
) -> None:
    """Test celery task with individual statistics update and empty qset."""
    update_one_user_statistics_task(user_id=active_user.pk, period=5)
    user_stats = resolve(UserStatisticsRepo).get_statistics(user=active_user)
    assert user_stats.average_answer_sec == 0


@pytest.mark.django_db
def test_bulk_update_user_statistics_task(
    mock_celery_tasks: dict[str, mock.Mock],
) -> None:
    """Test bulk statistics update."""
    update_user_statistics_task()
    mock_celery_tasks['group'].assert_called_once()
    mock_celery_tasks['group'].return_value.apply_async.assert_called_once()


@pytest.mark.django_db
def test_delete_one_survey_task(survey: Survey) -> None:
    """Test survey deletion celery task."""
    survey_id = survey.id
    task_result: EagerResult = delete_one_survey_task.delay(survey_id)
    task_result.get(timeout=5)
    assert task_result.state == 'SUCCESS'
    with pytest.raises(ObjectDoesNotExist):
        Survey.objects.get(pk=survey_id)


@pytest.mark.django_db
def test_delete_one_question_task(question: Question) -> None:
    """Test question deletion celery task."""
    question_id = question.id
    task_result: EagerResult = delete_one_question_task.delay(question_id)
    task_result.get(timeout=5)
    assert task_result.state == 'SUCCESS'
    with pytest.raises(ObjectDoesNotExist):
        Question.objects.get(pk=question_id)


@pytest.mark.django_db
def test_delete_marked_surveys_task(
    two_surveys_to_delete: list[Survey],
) -> None:
    """Test bulk surveys deletion celery task."""
    survey_ids = [survey.id for survey in two_surveys_to_delete]
    delete_marked_surveys_task.delay()
    for survey_id in survey_ids:
        with pytest.raises(ObjectDoesNotExist):
            Survey.objects.get(pk=survey_id)


@pytest.mark.django_db
def test_delete_marked_questions_task(
    two_questions_to_delete: list[Question],
) -> None:
    """Test bulk questions deletion celery task."""
    question_ids = [question.id for question in two_questions_to_delete]
    delete_marked_questions_task.delay()
    for question_id in question_ids:
        with pytest.raises(ObjectDoesNotExist):
            Question.objects.get(pk=question_id)
