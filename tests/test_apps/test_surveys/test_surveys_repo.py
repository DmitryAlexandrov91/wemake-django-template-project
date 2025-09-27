from collections.abc import Callable

import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import SurveyRepo, SurveyResultRepo
from server.apps.surveys.models import Question, Survey
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import (
    SurveyResultFactory,
    UserAnswerFactory,
)
from tests.plugins.users import UserFactory


@pytest.mark.django_db
def test_update_survey_partial_data(survey: Survey) -> None:
    """Test SurveyRepo update_survey method with partial data."""
    repo = resolve(SurveyRepo)
    original_description = survey.description

    updated_survey = repo.update_survey(
        survey=survey,
        title='Updated Title',
        description=None,
        department={'name': 'update name'},
    )

    assert updated_survey.pk == survey.pk
    assert updated_survey.title == 'Updated Title'
    assert updated_survey.description == original_description


@pytest.mark.django_db
def test_get_result_method(
    survey: Survey,
    surveys_survey_result_factory: SurveyResultFactory,
    surveys_user_answer_result_factory: UserAnswerFactory,
) -> None:
    """Test get_result_method of SurveyRepo."""
    repo = resolve(SurveyRepo)
    new_survey_result = surveys_survey_result_factory(survey=survey)
    surveys_user_answer_result_factory(survey_result=new_survey_result)
    survey_results = repo.get_results(survey.pk)
    assert len(survey_results) == 1
    assert survey_results[0].survey == survey


@pytest.mark.django_db
@pytest.mark.parametrize('department', ['Department2'], indirect=True)
def test_get_active_survey_for_user(
    department: Department,
    auth_user: CustomUser,
    create_surveys: Callable[[Department], Survey],
) -> None:
    """Testing active survey is found."""
    repo = resolve(SurveyRepo)
    user = auth_user
    active_survey = create_surveys(department)
    assert repo.get_active_survey_for_user(user=user) == active_survey


@pytest.mark.django_db
def test_create_user_survey_res(
    user_factory: UserFactory,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Create one active SurveyResult, set the pointer to the 1 question."""
    repo = resolve(SurveyResultRepo)
    questions = questions_batch(3)
    user = user_factory(
        username='User1',
        email='user1@mail.com',
        is_active=True,
        is_staff=False,
        tg_username='tg_username',
        department=questions[0].survey.department,
    )
    res = repo.get_or_create_user_survey_res(
        user=user, survey=questions[0].survey
    )
    assert res.current_question == questions[0].survey.questions.earliest('pk')
