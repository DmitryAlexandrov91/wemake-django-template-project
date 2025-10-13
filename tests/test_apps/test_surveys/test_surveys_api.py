from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.surveys.models import Survey
from tests.plugins.department_factory import DepartmentFactory

NAME = 'name'


@pytest.mark.django_db
def test_patch_success(
    survey: Survey,
    auth_client: APIClient,
    department_factory: DepartmentFactory,
) -> None:
    """Successfully partial updating a department."""
    url = reverse('surveys-detail', kwargs={'pk': survey.pk})
    new_department = department_factory(name='Department for update')
    payload = {
        NAME: 'Test_surveys_name',
        'comment': 'Test_surveys_descriptions',
        'department_name': new_department.name,
    }
    response = auth_client.patch(url, payload, format='json')
    response_data = response.json()

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response_data[NAME] == payload[NAME]
    assert response_data['comment'] == payload['comment']
    assert response_data['started_at'] == survey.start_date.isoformat()
    assert response_data['department']['name'] == payload['department_name']
