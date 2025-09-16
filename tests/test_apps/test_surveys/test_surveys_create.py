from http import HTTPStatus

import pytest
from django.test import Client

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
