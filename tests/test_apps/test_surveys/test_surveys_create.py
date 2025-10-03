from collections.abc import Callable
from http import HTTPStatus

import pytest
from django.core.exceptions import ValidationError
from django.test import Client

from server.apps.surveys.models import Question, Survey, SurveyQuestion
from server.apps.surveys.serializers_create import SurveyUpdateSerializer
from server.apps.users.models import CustomUser
from tests.plugins.surveys_survey import CREATE_SURVEY_URL
from tests.plugins.users_auth import LOGIN_URL
from tests.test_apps.test_surveys.services import get_survey_json
from tests.test_apps.test_users.services import get_user_json


@pytest.mark.django_db
@pytest.mark.parametrize(
    'nested_params',
    [True, False],
)
def test_success_survey_create(
    client: Client, user: CustomUser, password: str, *, nested_params: bool
) -> None:
    """Test creating survey instance."""
    client.post(LOGIN_URL, data=get_user_json(user.email, password))
    json_data = (
        get_survey_json()
        if nested_params
        else get_survey_json(answers_count=None)
    )
    response = client.post(
        CREATE_SURVEY_URL,
        data=json_data,
        content_type='application/json',
    )
    assert response.status_code == HTTPStatus.CREATED
    survey_data = response.json()
    assert survey_data is not None
    assert survey_data.get('questions')


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
