from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.models import Question, Survey
from tests.plugins.surveys_survey import SurveyFactory

URL_NAME = 'surveys-detail'
PATCH_FORMAT = 'json'
QUESTIONS_FIELD = 'questions'
FINISHED_AT_FIELD = 'finished_at'
PK_FIELD = 'pk'


@pytest.mark.django_db
def test_patch_questions_validation(
    surveys_survey_factory: SurveyFactory,
    auth_client: APIClient,
    consent_given_question: Question,
) -> None:
    """Cannot update questions if survey is not a draft."""
    survey = surveys_survey_factory(status=SurveyStatus.ACTIVE)
    url = reverse(URL_NAME, kwargs={PK_FIELD: survey.pk})
    payload = {QUESTIONS_FIELD: [{'id': consent_given_question.id}]}

    response = auth_client.patch(url, payload, format=PATCH_FORMAT)
    response_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert QUESTIONS_FIELD in response_data
    assert response_data[QUESTIONS_FIELD] == ['Можно менять только черновикам.']


@pytest.mark.django_db
def test_patch_finished_at_validation(
    surveys_survey_factory: SurveyFactory, auth_client: APIClient
) -> None:
    """Cannot update finished_at if survey is not draft or active."""
    survey = surveys_survey_factory(status=SurveyStatus.COMPLETED)
    url = reverse(URL_NAME, kwargs={PK_FIELD: survey.pk})
    payload = {FINISHED_AT_FIELD: '2025-12-31'}

    response = auth_client.patch(url, payload, format=PATCH_FORMAT)
    response_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert FINISHED_AT_FIELD in response_data
    assert response_data['finished_at'] == [
        'Дату окончания можно изменить опросам '
        'чей статус: активный или черновик'
    ]


@pytest.mark.django_db
def test_patch_status_validation(
    surveys_survey_factory: SurveyFactory, auth_client: APIClient
) -> None:
    """Cannot change survey status from active/completed to draft."""
    survey = surveys_survey_factory(status=SurveyStatus.ACTIVE)
    url = reverse(URL_NAME, kwargs={PK_FIELD: survey.pk})
    payload = {'status': SurveyStatus.DRAFT}

    response = auth_client.patch(url, payload, format=PATCH_FORMAT)
    response_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'status' in response_data
    assert response_data['status'] == [
        'Невозможно поменять статус активного '
        'или завершенного опроса на черновик'
    ]


@pytest.mark.django_db
def test_update_survey_with_invalid_question_id(
    auth_client: APIClient,
    survey: Survey,
) -> None:
    """Validate question IDs exist in the database."""
    survey.end_date = timezone.now().date() + timedelta(days=1)
    payload = {
        QUESTIONS_FIELD: [{'id': 0}],
        FINISHED_AT_FIELD: survey.end_date + timedelta(days=2),
    }
    url = reverse(URL_NAME, kwargs={PK_FIELD: survey.pk})
    response = auth_client.patch(url, payload, format=PATCH_FORMAT)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Передан несуществующий вопрос'
