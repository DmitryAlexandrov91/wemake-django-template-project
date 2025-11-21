from collections.abc import Callable
from http import HTTPStatus

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.surveys.models import Question, Survey, SurveyQuestion
from server.apps.surveys.usecases.inform_recipients import survey_notification
from tests.plugins.surveys import QuestionFactory
from tests.plugins.surveys_survey import CREATE_SURVEY_URL


@pytest.mark.django_db
def test_success_survey_create(
    auth_client: APIClient,
    department: Department,
    surveys_question_factory: QuestionFactory,
) -> None:
    """Test creating survey instance."""
    payload = {
        'name': 'Тестовый',
        'comment': 'Комментарий',
        'started_at': '2025-10-09',
        'finished_at': '2025-10-10',
        'department_name': department.name,
        'questions': [{'id': surveys_question_factory().id}],
    }

    response = auth_client.post(
        CREATE_SURVEY_URL,
        data=payload,
        content_type='application/json',
    )
    assert response.status_code == HTTPStatus.CREATED
    survey_data = response.json()
    assert survey_data is not None
    assert 'questions' in survey_data


@pytest.mark.django_db
def test_create_survey_with_invalid_question_id(
    auth_client: APIClient,
    department: Department,
) -> None:
    """Validate question IDs exist in the database."""
    payload = {
        'name': 'Тестовый',
        'comment': 'Комментарий',
        'started_at': '2025-10-09',
        'finished_at': '2025-10-10',
        'department_name': department.name,
        'questions': [{'id': 0}],
    }
    response = auth_client.post(
        CREATE_SURVEY_URL,
        data=payload,
        content_type='application/json',
    )
    assert response.status_code == 404
    assert response.json()['detail'] == 'Передан несуществующий вопрос'


@pytest.mark.django_db
def test_survey_question_unique_text_violation(
    survey: Survey,
    surveys_question_factory: Callable[..., Question],
) -> None:
    """SurveyQuestion.clean: no duplicated question text in one survey."""
    question1 = surveys_question_factory(text='Same text')
    question2 = surveys_question_factory(text='Same text')  # Same text.

    SurveyQuestion.objects.create(survey=survey, question=question1)

    survey_question = SurveyQuestion(survey=survey, question=question2)
    with pytest.raises(
        ValidationError, match='already has a question with this text'
    ):
        survey_question.save()


@pytest.mark.django_db
def test_survey_notification_no_bot_username(
    monkeypatch: pytest.MonkeyPatch,
    survey: Survey,
) -> None:
    """Test survey_notification raises ValueError if bot username is None."""
    monkeypatch.setattr(
        'server.apps.surveys.usecases.inform_recipients.get_bot_username',
        lambda: None,
    )
    with pytest.raises(ValueError, match=r'No bot username received\.'):
        survey_notification(survey)
