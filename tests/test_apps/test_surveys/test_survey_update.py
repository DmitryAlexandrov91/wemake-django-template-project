from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.surveys import choices, models, serializers_create
from server.apps.surveys.infra.repository import SurveyRepo, SurveySaveRepo
from server.apps.surveys.usecases.inform_recipients import survey_notification
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.users_requests import RequestMock


@pytest.mark.django_db
def test_survey_update_serializer_integration(
    survey: models.Survey, department: Department
) -> None:
    """Integration test for SurveyUpdateSerializer with actual repo."""
    validated_data = {
        'title': 'Updated Title',
        'department_name': department,
    }

    serializer = serializers_create.SurveyUpdateSerializer()
    upd_survey = serializer.update(survey, validated_data)

    assert upd_survey.pk == survey.pk
    assert upd_survey.title == 'Updated Title'


@pytest.mark.django_db
def test_update_survey_partial_data(survey: models.Survey) -> None:
    """Test SurveyRepo update_survey method with partial data."""
    repo = resolve(SurveyRepo)
    original_description = survey.description

    updated_survey = repo.update_survey(
        survey=survey,
        title='New Title',
        description=None,
    )

    assert updated_survey.pk == survey.pk
    assert updated_survey.title == 'New Title'
    assert updated_survey.description == original_description


@pytest.mark.django_db
def test_update_survey_without_department_name(survey: models.Survey) -> None:
    """Test updating survey without changing department."""
    repo = resolve(SurveyRepo)
    original_department = survey.department

    updated_survey = repo.update_survey(
        survey=survey,
        title='New_Title',
        description='Updated description',
    )

    assert updated_survey.title == 'New_Title'
    assert updated_survey.description == 'Updated description'
    assert updated_survey.department == original_department


@pytest.mark.django_db
@patch('telebot.TeleBot')
def test_survey_notification_success(
    mock_telebot: Mock,
    survey: models.Survey,
    department: Department,
    three_users_to_process: list[CustomUser],
    mocked_send_survey_invitation: Mock,
) -> None:
    """Test successful survey invitation mailing."""
    mock_bot_instance = mock_telebot.return_value
    mock_me_result = Mock()
    mock_me_result.username = 'test_bot'
    mock_bot_instance.get_me.return_value = mock_me_result

    survey.department = department
    survey.save()

    survey_notification(survey)

    assert mocked_send_survey_invitation.call_count == 3


@pytest.mark.django_db
@patch('server.apps.surveys.views.survey_notification')
def test_partial_update_calls_survey_notification(
    mock_survey_notification: Mock,
    auth_client: APIClient,
    survey: models.Survey,
    survey_activation_request: RequestMock,
) -> None:
    """Test survey notification starts."""
    assert survey.status == choices.SurveyStatus.DRAFT
    url = reverse('surveys-detail', kwargs={'pk': survey.pk})
    response = auth_client.patch(
        url, survey_activation_request.data, format='json'
    )

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert (
        resolve(SurveySaveRepo).get_by_pk(survey.id).status
        == choices.SurveyStatus.ACTIVE
    )
    mock_survey_notification.assert_called_once()
