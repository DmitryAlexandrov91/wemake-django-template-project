from collections.abc import Callable
from http import HTTPStatus

import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.surveys.models import Question, Survey, SurveyQuestion
from server.apps.surveys.serializers_create import SurveyUpdateSerializer
from tests.plugins.surveys_survey import CREATE_SURVEY_URL


@pytest.mark.django_db
def test_success_survey_create(
    auth_client: APIClient, department: Department
) -> None:
    """Test creating survey instance."""
    payload = {
        'name': 'Тестовый',
        'comment': 'Комментарий',
        'started_at': '2025-10-09',
        'finished_at': '2025-10-10',
        'department_name': department.name,
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
def test_survey_update_serializer_integration(survey: Survey) -> None:
    """Integration test for SurveyUpdateSerializer with actual repo."""
    validated_data = {
        'title': 'Updated Title',
        'department': {'name': 'New Department Name'},
    }

    serializer = SurveyUpdateSerializer()
    upd_survey = serializer.update(survey, validated_data)

    assert upd_survey.pk == survey.pk
    assert upd_survey.title == 'Updated Title'


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
