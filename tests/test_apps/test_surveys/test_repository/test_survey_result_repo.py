from collections.abc import Callable

import pytest
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
    SurveySaveRepo,
)
from server.apps.surveys.models import Question, Survey
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import SurveyResultFactory, UserAnswerFactory
from tests.plugins.users import UserFactory


@pytest.mark.django_db
def test_get_result_method(
    survey: Survey,
    surveys_survey_result_factory: SurveyResultFactory,
    surveys_user_answer_result_factory: UserAnswerFactory,
) -> None:
    """Test get_result_method of SurveyRepo."""
    new_survey_result = surveys_survey_result_factory(survey=survey)
    surveys_user_answer_result_factory(survey_result=new_survey_result)
    survey_results = resolve(SurveyRepo).get_results(survey.pk)
    assert len(survey_results) == 1
    assert survey_results[0].survey == survey


@pytest.mark.django_db
def test_create_user_survey_res(
    user_factory: UserFactory,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Create one active SurveyResult, set the pointer to the 1st question."""
    first_question_surveys = questions_batch(3)[0].surveys.all()
    assert first_question_surveys.exists()
    survey = first_question_surveys[0]
    user = user_factory(
        username='User1',
        email='user1@mail.com',
        is_active=True,
        is_staff=False,
        tg_username='tg_username',
        department=survey.department,
    )
    res = resolve(SurveyResultRepo).get_or_create_user_survey_res(
        user=user, survey=survey
    )
    related_questions = survey.questions.order_by('pk')
    assert res.current_question == related_questions.first()


@pytest.mark.django_db
def test_completed_surveys_returns_results(
    auth_user: CustomUser,
    survey: Survey,
    surveys_survey_result_factory: SurveyResultFactory,
    surveys_user_answer_result_factory: UserAnswerFactory,
) -> None:
    """Ensure get_completed_surveys returns all survey results for a user."""
    new_survey_result = surveys_survey_result_factory(
        survey=survey, user=auth_user, bot_state='completed'
    )
    surveys_user_answer_result_factory(survey_result=new_survey_result)
    results_survyes = resolve(SurveyResultRepo).get_completed_surveys(auth_user)
    assert results_survyes.count() == 1
    assert new_survey_result in results_survyes


@pytest.mark.django_db
def test_get_by_pk(survey: Survey) -> None:
    """Test the `get_by_pk()` method of SurveySaveRepo."""
    repo = resolve(SurveySaveRepo)
    survey_obj = repo.get_by_pk(pk=survey.id)
    assert survey_obj == survey


@pytest.mark.django_db
def test_get_all_expired_ids(
    department: Department,
    create_surveys: Callable[[Department], Survey],
) -> None:
    """Test getting expired surveys only."""
    now_date = timezone.now().date()
    create_surveys(department)
    expired_survey = Survey.objects.get(
        status=SurveyStatus.ACTIVE, end_date__lt=now_date
    )
    res = resolve(SurveySaveRepo).get_all_expired_ids()
    expected_ids = [expired_survey.id]
    assert isinstance(res, list)
    assert res == expected_ids
