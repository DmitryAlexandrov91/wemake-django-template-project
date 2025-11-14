from collections.abc import Callable

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.company.models import Department
from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.filters import STATUS_MAPPING
from server.apps.surveys.models.surveys import Survey
from tests.plugins.fakery import FakeryM

SURVEY_URL = reverse('surveys-list')
STATUS = 'status'


@pytest.mark.django_db
def test_survey_status_mapping(
    fakery_m: FakeryM[Survey],
    auth_client: APIClient,
) -> None:
    """Test ensure that mapping filter works correctly."""
    fakery_m(Survey)(is_favorite=True, status=SurveyStatus.COMPLETED)
    fakery_m(Survey)(status=SurveyStatus.DRAFT, is_favorite=False)
    fakery_m(Survey)(status=SurveyStatus.ARCHIVED, is_favorite=False)

    surveys = Survey.objects.all()
    assert len(surveys) == 3

    for status in STATUS_MAPPING:
        response = auth_client.get(SURVEY_URL, {STATUS: status})
        response_data = response.json()['data']
        assert len(response_data) == 1


@pytest.mark.django_db
def test_active_survey_filter(
    auth_client: APIClient,
    create_surveys: Callable[[Department], Survey],
    department: Department,
) -> None:
    """Test ensure that survey filter status=active works correctly."""
    create_surveys(department=department)  # type: ignore[call-arg]
    active_survey = Survey.objects.get(status=SurveyStatus.ACTIVE)

    response = auth_client.get(SURVEY_URL, {STATUS: 'active'})
    response_data = response.json()['data'][0]

    assert response_data['name'] == active_survey.title
    assert response_data[STATUS] == active_survey.status


@pytest.mark.django_db
def test_finished_survey_filter(
    auth_client: APIClient,
    create_surveys: Callable[[Department], Survey],
    department: Department,
) -> None:
    """Test ensure that survey filter status=finished works correctly."""
    create_surveys(department=department)  # type: ignore[call-arg]
    completed_survey = Survey.objects.get(status=SurveyStatus.COMPLETED)

    response = auth_client.get(SURVEY_URL, {STATUS: 'finished'})
    response_data = response.json()['data'][0]

    assert response_data['name'] == completed_survey.title
    assert response_data[STATUS] == completed_survey.status
