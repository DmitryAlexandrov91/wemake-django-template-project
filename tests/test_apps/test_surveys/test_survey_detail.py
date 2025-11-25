import pytest
from django.test import Client
from rest_framework import status

from server.apps.surveys.models import Survey


@pytest.mark.django_db
def test_get_survey_detail(
    auth_client: Client, surveys_with_answers_to_questions: Survey
) -> None:
    """Test GET /api/surveys/<id>/ returns survey with questions and answers."""
    survey = surveys_with_answers_to_questions

    response = auth_client.get(f'/api/surveys/{survey.id}/')
    assert response.status_code == status.HTTP_200_OK

    survey_response_data = response.json()
    assert survey_response_data['id'] == survey.id
    assert len(survey_response_data['questions']) == 1
    assert survey_response_data['questions'][0]['user_answers']
