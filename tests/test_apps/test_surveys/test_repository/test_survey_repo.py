from collections.abc import Callable

import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import Survey, SurveyQuestion
from server.apps.users.models import CustomUser
from server.di import resolve

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
) -> None:
    """Create survey with questions and answers."""
    repo = SurveyRepo()
    survey_data = {
        'title': 'Test survey',
        'description': 'Test desc',
        'department_name': department,
        'start_date': '2025-10-3',
        'questions': [
            {
                TEXT: 'Question 1',
                IS_FAVORITE: False,
                QUESTION_TYPE: SCORE,
                ANSWERS: [
                    {TEXT: 'Answer 1'},
                    {TEXT: 'Answer 2'},
                ],
            },
            {
                TEXT: 'Question 2',
                IS_FAVORITE: True,
                QUESTION_TYPE: SCORE,
                ANSWERS: [
                    {TEXT: 'Answer 3'},
                ],
            },
        ],
    }

    survey = repo.create_survey_with_questions(survey_data)

    assert Survey.objects.filter(pk=survey.pk).exists()
    assert survey.questions.count() == 2
    for question in survey.questions.all():
        assert SurveyQuestion.objects.filter(
            survey=survey, question=question
        ).exists()
        answer_count = 2 if question.text == 'Question 1' else 1
        assert question.answer_options.count() == answer_count


@pytest.mark.django_db
def test_create_survey_with_questions_no_answers(
    department: Department,
) -> None:
    """Create survey with questions but without answers."""
    survey_data = {
        'title': 'Test survey',
        'description': 'Test desc',
        'department_name': department,
        'start_date': '2025-10-3',
        'questions': [
            {
                TEXT: 'Question 1',
                IS_FAVORITE: False,
                QUESTION_TYPE: SCORE,
                ANSWERS: [],
            },
            {
                TEXT: 'Question 2',
                IS_FAVORITE: True,
                QUESTION_TYPE: SCORE,
                ANSWERS: [],
            },
        ],
    }

    survey = resolve(SurveyRepo).create_survey_with_questions(survey_data)

    assert Survey.objects.filter(pk=survey.pk).exists()
    assert survey.questions.count() == 2
    for question in survey.questions.all():
        assert question.answer_options.count() == 0
