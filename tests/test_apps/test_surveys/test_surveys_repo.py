from collections.abc import Callable
from datetime import date

import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import SurveyRepo, SurveyResultRepo
from server.apps.surveys.models import (
    Question,
    Survey,
    SurveyQuestion,
)
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import (
    SurveyResultFactory,
    UserAnswerFactory,
)
from tests.plugins.users import UserFactory

NAME = 'name'
DEPARTMENT = 'department'
TEXT = 'text'
QUESTION_TYPE = 'question_type'


@pytest.mark.django_db
def test_update_survey_partial_data(survey: Survey) -> None:
    """Test SurveyRepo update_survey method with partial data."""
    repo = resolve(SurveyRepo)
    original_description = survey.description

    updated_survey = repo.update_survey(
        survey=survey,
        title='Updated Title',
        description=None,
        department={NAME: 'update name'},
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
def test_create_user_survey_res(
    user_factory: UserFactory,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Create one active SurveyResult, set the pointer to the 1 question."""
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
def test_create_survey_with_questions_and_answers() -> None:
    """Create survey with questions and answers."""
    repo = SurveyRepo()
    survey_data = {
        'title': 'Test survey',
        'description': 'Test desc',
        DEPARTMENT: {NAME: 'Test dept'},
        'start_date': date(2025, 10, 3),
        'questions': [
            {
                TEXT: 'Question 1',
                'is_favorite': False,
                QUESTION_TYPE: 'score',
                'answers': [
                    {TEXT: 'Answer 1'},
                    {TEXT: 'Answer 2'},
                ],
            },
            {
                TEXT: 'Question 2',
                'is_favorite': True,
                QUESTION_TYPE: 'score',
                'answers': [
                    {TEXT: 'Answer 3'},
                ],
            },
        ],
    }

    survey = repo.create(survey_data.copy())

    assert Survey.objects.filter(pk=survey.pk).exists()
    assert survey.questions.count() == 2
    for question in survey.questions.all():
        assert SurveyQuestion.objects.filter(
            survey=survey, question=question
        ).exists()
        answer_count = 2 if question.text == 'Question 1' else 1
        assert question.answer_options.count() == answer_count
    assert survey.department.name == 'Test dept'


@pytest.mark.django_db
def test_create_survey_without_questions() -> None:
    """Create survey without questions."""
    repo = SurveyRepo()
    survey_data = {
        'title': 'Survey without questions',
        'description': '',
        DEPARTMENT: {NAME: 'No Questions Dept'},
        'start_date': date(2025, 10, 3),
        'questions': [],
    }
    survey = repo.create(survey_data.copy())
    assert Survey.objects.filter(pk=survey.pk).exists()
    assert survey.questions.count() == 0
    assert survey.department.name == 'No Questions Dept'


@pytest.mark.django_db
def test_create_survey_with_question_no_answers() -> None:
    """Create survey with questions without answers."""
    repo = SurveyRepo()
    survey_data = {
        'title': 'Survey empty answers',
        'description': '',
        DEPARTMENT: {NAME: 'Empty answers dept'},
        'start_date': date(2025, 10, 3),
        'questions': [
            {
                TEXT: 'Lonely Question',
                'is_favorite': False,
                QUESTION_TYPE: 'score',
                'answers': [],
            }
        ],
    }
    survey = repo.create(survey_data.copy())
    question = survey.questions.first()
    assert question
    assert question.text == 'Lonely Question'
    assert question.answer_options.count() == 0
    assert SurveyQuestion.objects.filter(
        survey=survey, question=question
    ).exists()
