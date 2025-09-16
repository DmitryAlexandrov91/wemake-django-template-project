from collections.abc import Callable
from http import HTTPStatus

import pytest
from django.test import Client

from server.apps.company.models import Department
from server.apps.surveys import paginators, serializers_list
from server.apps.surveys.choices import QuestionType
from server.apps.surveys.models import (
    AnswerOption,
)
from server.apps.users.models import CustomUser
from tests.plugins import (
    department_factory,
    surveys,
    surveys_survey,
    users_auth,
)
from tests.test_apps.test_surveys.services import build_survey
from tests.test_apps.test_users.services import get_user_json

DATA_ATTR = 'data'
NAME_ATTR = 'name'
FILTER_ATTR = 'filter'
ID_ATTR = 'id'


@pytest.mark.django_db
def test_get_all_surveys_response(
    client: Client, user: CustomUser, password: str
) -> None:
    """Test success response status of `api/surveys`."""
    client.post(users_auth.LOGIN_URL, data=get_user_json(user.email, password))
    response = client.get(surveys_survey.GET_ALL_SURVEYS_URL)
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    surveys_data = response_data.get(DATA_ATTR, {})
    assert surveys_data is not None


@pytest.mark.django_db
def test_paginator_page_is_none() -> None:
    """Test event with paginator.page is None."""
    paginator = paginators.CustomPaginator()
    paginator_response = paginator.get_paginated_response([{ID_ATTR: 1}])
    assert paginator_response.status_code == HTTPStatus.OK
    response_data = paginator_response.data
    assert response_data[DATA_ATTR] == [{ID_ATTR: 1}]
    assert 'page' not in response_data
    assert 'per_page' not in response_data


@pytest.mark.django_db
def test_filter_query_params(  # noqa: WPS210
    client: Client,
    user: CustomUser,
    password: str,
    surveys_survey_factory: surveys_survey.SurveyFactory,
    department_factory: department_factory.DepartmentFactory,
) -> None:
    """Test filtering."""
    client.post(users_auth.LOGIN_URL, data=get_user_json(user.email, password))
    favorite = build_survey(
        'favorite', department_factory, surveys_survey_factory
    )
    drafts = build_survey('drafts', department_factory, surveys_survey_factory)
    finished = build_survey(
        'finished', department_factory, surveys_survey_factory
    )
    archive = build_survey(
        'archive', department_factory, surveys_survey_factory
    )
    favorite_response = client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'favorite'}
    )
    survey = favorite_response.json()[DATA_ATTR][0]
    assert survey[NAME_ATTR] == favorite.title
    drafts_response = client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'drafts'}
    )
    survey = drafts_response.json()[DATA_ATTR][0]
    assert survey[NAME_ATTR] == drafts.title
    finished_response = client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'finished'}
    )
    surveys = finished_response.json()[DATA_ATTR]
    assert all(
        survey[NAME_ATTR] in {archive.title, finished.title}
        for survey in surveys
    )
    archive_response = client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'archive'}
    )
    survey = archive_response.json()[DATA_ATTR][0]
    assert survey[NAME_ATTR] == archive.title
    all_response = client.get(surveys_survey.GET_ALL_SURVEYS_URL)
    surveys = all_response.json()[DATA_ATTR]
    assert len(surveys) == 4


@pytest.mark.django_db
@pytest.mark.parametrize('bunch', [True, False])
def test_response_with_text_answer(  # noqa: WPS211, WPS210
    user: CustomUser,
    surveys_survey_factory: surveys_survey.SurveyFactory,
    surveys_question_factory: surveys.QuestionFactory,
    department: Department,
    surveys_survey_result_factory: surveys_survey.SurveyResultFactory,
    surveys_user_answer_result_factory: surveys_survey.UserAnswerFactory,
    surveys_answer_option_batch: Callable[[int], list[AnswerOption]],
    bunch: bool,  # noqa: FBT001
) -> None:
    """Test user_answer response for text_answer."""
    survey = surveys_survey_factory(department=department)
    user_answer_params: dict[str, str] = {}
    if not bunch:
        user_answer_params['text_answer'] = 'Some comment'
    user_answer = surveys_user_answer_result_factory(
        survey_result=surveys_survey_result_factory(user=user, survey=survey),
        question=surveys_question_factory(
            survey=survey,
            question_type=QuestionType.SCORE,
        ),
        **user_answer_params,  # type: ignore[arg-type]
    )
    question = surveys_question_factory(
        survey=survey,
        question_type=QuestionType.SCORE,
    )
    if bunch:
        options = surveys_answer_option_batch(2)
        for option in options:
            option.question = question
            option.save()
        user_answer.selected_options.set(options)
    serialized = serializers_list.UserAnswersListSerializer(user_answer).data
    expected_result = ['Option 0', 'Option 1'] if bunch else 'Some comment'
    assert serialized['result'] == expected_result
    assert serialized['employer'][ID_ATTR] == user.id
