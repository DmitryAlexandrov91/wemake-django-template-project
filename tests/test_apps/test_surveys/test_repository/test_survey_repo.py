from collections.abc import Callable

import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import Survey, SurveyQuestion
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys import QuestionFactory

NAME = 'name'
DEPARTMENT = 'department'
TEXT = 'text'
QUESTION_TYPE = 'question_type'
SCORE = 'score'
IS_FAVORITE = 'is_favorite'
ANSWERS = 'answers'


@pytest.mark.django_db
@pytest.mark.parametrize(DEPARTMENT, ['Department2'], indirect=True)
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
@pytest.mark.parametrize(DEPARTMENT, ['Department2'], indirect=True)
def test_get_active_survey_for_user_by_id(
    department: Department,
    auth_user: CustomUser,
    create_surveys: Callable[[Department], Survey],
) -> None:
    """Test getting active survey by user and id."""
    repo = resolve(SurveyRepo)
    active_survey = create_surveys(department)
    assert (
        repo.get_active_survey_for_user_by_id(
            user=auth_user, survey_id=active_survey.pk
        )
        == active_survey
    )


@pytest.mark.django_db
def test_create_survey_with_questions_and_answers(
    department: Department,
    surveys_question_factory: QuestionFactory,
) -> None:
    """Create survey with questions and answers."""
    questions = [
        surveys_question_factory(text='Question 1'),
        surveys_question_factory(text='Question 2'),
    ]
    survey_data = {
        'title': 'Test survey',
        'description': 'Test desc',
        'department_name': department,
        'start_date': '2025-10-3',
        'questions': [{'id': question.id} for question in questions],
    }

    survey = SurveyRepo().create_survey_with_questions(survey_data)

    assert Survey.objects.filter(pk=survey.pk).exists()
    assert survey.questions.count() == 2
    for question in survey.questions.all():
        assert SurveyQuestion.objects.filter(
            survey=survey, question=question
        ).exists()
