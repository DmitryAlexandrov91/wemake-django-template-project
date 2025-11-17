from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any
from unittest import mock

import pytest
from django.utils import timezone
from pytest_mock import MockerFixture

from server.apps.company.models import Department
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyResult,
    UserAnswer,
)
from server.apps.users.models import CustomUser
from tests.plugins import department_factory, surveys_survey


@pytest.fixture
def create_surveys(
    surveys_survey_factory: surveys_survey.SurveyFactory,
    department_factory: department_factory.DepartmentFactory,
) -> Callable[[Department], Survey]:
    """Fixture for creating all survey types."""

    def factory(department: Department) -> Survey:
        today = timezone.now().date()
        surveys_survey_factory(
            title='Another department survey',
            description='Another survey text',
            start_date=today,
            end_date=today + timedelta(days=30),
            department=department_factory(name='Department1'),
            is_favorite=False,
            status='draft',
        )
        active_survey = surveys_survey_factory(
            title='Active survey',
            description='Active survey text',
            start_date=today,
            end_date=today + timedelta(days=30),
            department=department,
            is_favorite=False,
            status='active',
        )
        surveys_survey_factory(
            title='Ended survey',
            description='Ended survey text',
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            department=department,
            is_favorite=False,
            status='completed',
        )
        surveys_survey_factory(
            title='Expired survey',
            description='Expired survey text',
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=1),
            department=department,
            is_favorite=False,
            status='active',
        )
        return active_survey

    return factory


@pytest.fixture
def question_with_two_surveys(  # noqa: WPS234
    surveys_question_factory: Callable[..., Question],
    two_surveys: list[Survey],
) -> Callable[[dict[str, Any]], tuple[Question, list[Survey]]]:  # noqa: WPS221
    """Fixture for creating a question with two surveys."""

    def factory(
        question_params: dict[str, Any] | None = None,
    ) -> tuple[Question, list[Survey]]:
        params_data = question_params or {}
        question = surveys_question_factory(**params_data)
        question.surveys.set(two_surveys)
        return question, two_surveys

    return factory


@pytest.fixture
def survey_result_with_three_questions(
    surveys_survey_result_factory: Callable[[], SurveyResult],
    surveys_question_factory: Callable[..., Question],
) -> tuple[SurveyResult, list[Question]]:
    """Fixture prepares survey result and three questions."""
    survey_result = surveys_survey_result_factory()
    questions = [
        surveys_question_factory(),
        surveys_question_factory(),
        surveys_question_factory(),
    ]
    for question in questions:
        question.surveys.add(survey_result.survey)
        question.save()
    survey_result.current_question = questions[0]
    survey_result.save(update_fields=['current_question'])
    return survey_result, questions


@pytest.fixture
def survey_results_for_user(
    active_user: CustomUser,
    surveys_survey_result_factory: Callable[[], SurveyResult],
) -> tuple[CustomUser, int]:
    """Fixture creates five completed SurveyResult objects for the user."""
    now = timezone.now()
    delta_sum = 0
    questions = 0
    for count in range(5):
        survey_result = surveys_survey_result_factory()
        survey_result.user = active_user
        survey_result.current_question = None
        survey_result.completed_questions = count + 1
        survey_result.save()
        SurveyResult.objects.filter(id=survey_result.id).update(
            started_at=now - timedelta(days=count),
            updated_at=(
                now - timedelta(days=count) + timedelta(seconds=100 + count)
            ),
        )
        delta_sum += 100 + count
        questions += survey_result.completed_questions

    return active_user, int(delta_sum // questions)


@pytest.fixture
def mock_statistics_mocks(mocker: MockerFixture) -> dict[str, mock.Mock]:
    """Fixture for statistic mocks."""
    mock_task = mocker.patch(
        'server.apps.surveys.tasks.update_user_statistics_task.delay'
    )
    mock_get_stat_settings = mocker.patch(
        'server.apps.surveys.infra.repository.UserStatisticsRepo.get_stat_settings'
    )
    mock_settings = mock.Mock()
    mock_settings.survey_response_avg_period = 5
    mock_get_stat_settings.return_value = mock_settings
    return {'mock_task': mock_task, 'mock_settings': mock_settings}


@pytest.fixture
def mock_celery_tasks(mocker: MockerFixture) -> dict[str, mock.Mock]:
    """Mocking Celery."""
    mock_group = mocker.patch('server.apps.surveys.tasks.tasks.group')
    mock_update_task = mocker.patch(
        'server.apps.surveys.tasks.update_user_statistics_task'
    )
    mock_signature = mocker.Mock()
    mock_update_task.s = mocker.Mock(return_value=mock_signature)
    return {
        'group': mock_group,
        'update_task': mock_update_task,
        'signature': mock_signature,
    }


@pytest.fixture
def user_answer_complex(
    survey_result_with_three_questions: tuple[SurveyResult, list[Question]],
    surveys_answer_option_factory: Callable[[], AnswerOption],
    surveys_question_factory: Callable[..., Question],
    auth_user: CustomUser,
) -> UserAnswer:
    """Fixture creates a UserAnswer object with connected objects."""
    survey_result, _ = survey_result_with_three_questions
    survey_result.user = auth_user
    survey_result.save()

    question = surveys_question_factory()
    answer_option = surveys_answer_option_factory()
    question.surveys.add(survey_result.survey)
    question.save()

    user_answer = UserAnswer.objects.create(
        survey_result=survey_result,
        question=question,
        text_answer='Test answer text',
    )
    user_answer.selected_options.add(answer_option)
    return user_answer
