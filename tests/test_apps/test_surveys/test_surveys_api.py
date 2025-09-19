from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.surveys.models import Survey

NAME = 'name'


@pytest.mark.django_db
def test_patch_success(survey: Survey, auth_client: APIClient) -> None:
    """Successfully partial updating a department."""
    url = reverse('surveys-detail', kwargs={'pk': survey.pk})
    payload = {
        NAME: 'Test_surveys_name',
        'comment': 'Test_surveys_descriptions',
        'department': {'department_name': 'update name'},
    }
    response = auth_client.patch(url, payload, format='json')
    response_data = response.json()

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response_data[NAME] == payload[NAME]
    assert response_data['comment'] == payload['comment']
    assert response_data['started_at'] == survey.start_date.isoformat()
    assert (
        response_data['department']['name']
        == payload['department']['department_name']  # type: ignore[index]
    )
