from collections.abc import Callable
from datetime import timedelta
from http import HTTPStatus

import pytest
from django.test import Client
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys import (
    choices,
    models,
    paginators,
    serializers_list,
    serializers_report,
)
from server.apps.users.models import CustomUser
from tests.plugins import (
    department_factory,
    surveys,
    surveys_survey,
)
from tests.test_apps.test_surveys.services import build_survey

DATA_ATTR = 'data'
NAME_ATTR = 'name'
FILTER_ATTR = 'status'
ID_ATTR = 'id'


@pytest.mark.django_db
def test_get_all_surveys_response(
    auth_client: Client,
) -> None:
    """Test success response status of `api/surveys`."""
    response = auth_client.get(surveys_survey.GET_ALL_SURVEYS_URL)
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
    auth_client: Client,
    surveys_survey_factory: surveys_survey.SurveyFactory,
    department_factory: department_factory.DepartmentFactory,
) -> None:
    """Test filtering."""
    active = build_survey('active', department_factory, surveys_survey_factory)
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

    favorite_response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'favorite'}
    )
    survey = favorite_response.json()[DATA_ATTR][0]
    assert survey[NAME_ATTR] == favorite.title

    drafts_response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'drafts'}
    )
    survey = drafts_response.json()[DATA_ATTR][0]
    assert survey['status'] == drafts.status

    finished_response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'finished'}
    )
    survey = finished_response.json()[DATA_ATTR][0]
    assert survey[NAME_ATTR] == finished.title

    archive_response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'archive'}
    )
    surveys = archive_response.json()[DATA_ATTR][0]
    assert surveys[NAME_ATTR] == archive.title

    active_response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {FILTER_ATTR: 'active'}
    )
    surveys = active_response.json()[DATA_ATTR][0]
    assert surveys[NAME_ATTR] == active.title


@pytest.mark.django_db
@pytest.mark.parametrize('bunch', [True, False])
def test_response_with_text_answer(  # noqa: WPS211, WPS210
    user: CustomUser,
    surveys_survey_factory: surveys_survey.SurveyFactory,
    surveys_question_factory: surveys.QuestionFactory,
    department: Department,
    surveys_survey_result_factory: surveys_survey.SurveyResultFactory,
    surveys_user_answer_result_factory: surveys_survey.UserAnswerFactory,
    surveys_answer_option_batch: Callable[[int], list[models.AnswerOption]],
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
            surveys={survey},
            question_type=choices.QuestionType.SCORE,
        ),
        **user_answer_params,  # type: ignore[arg-type]
    )
    question = surveys_question_factory(
        surveys={survey},
        question_type=choices.QuestionType.SCORE,
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


@pytest.mark.django_db
def test_get_survey_sec(
    surveys_survey_result_factory: surveys_survey.SurveyResultFactory,
    surveys_question_factory: Callable[..., models.Question],
) -> None:
    """Ensure serializer calculates time difference correctly."""
    survey_result = surveys_survey_result_factory()
    start_time = timezone.now()
    t_delta = timedelta(seconds=1000)
    end_time = start_time + t_delta
    models.SurveyResult.objects.filter(pk=survey_result.pk).update(
        current_question=surveys_question_factory(survey=survey_result.survey),
        started_at=start_time,
        updated_at=end_time,
    )
    survey_result.refresh_from_db()
    serializer = serializers_report.SurveyTimeReportSerializer(
        instance=survey_result
    )
    assert serializer.get_survey_sec(survey_result) == t_delta.total_seconds()


@pytest.mark.django_db
def test_search_query_params(
    surveys_survey_factory: surveys_survey.SurveyFactory, auth_client: Client
) -> None:
    """Test search param for survey."""
    for title in ('First', 'Second', 'Third'):
        surveys_survey_factory(title=f'{title} Survey')

    response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {'search': 'survey'}
    )
    assert len(response.json()['data']) == 3

    response = auth_client.get(
        surveys_survey.GET_ALL_SURVEYS_URL, {'search': 'First'}
    )
    assert len(response.json()['data']) == 1
