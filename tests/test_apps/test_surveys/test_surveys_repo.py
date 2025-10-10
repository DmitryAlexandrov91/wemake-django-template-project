from collections.abc import Callable

import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import SurveyRepo, SurveyResultRepo
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyQuestion,
)
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import (
    SurveyFactory,
    SurveyResultFactory,
    UserAnswerFactory,
)
from tests.plugins.users import UserFactory

NAME = 'name'
DEPARTMENT = 'department'
TEXT = 'text'
QUESTION_TYPE = 'question_type'
SCORE = 'score'
IS_FAVORITE = 'is_favorite'
ANSWERS = 'answers'


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
def test_create_survey_with_questions_and_answers(
    department: Department,
) -> None:
    """Create survey with questions and answers."""
    repo = SurveyRepo()
    survey_data = {
        'title': 'Test survey',
        'description': 'Test desc',
        'department_name': department.name,
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

    survey = repo.create(survey_data)

    assert Survey.objects.filter(pk=survey.pk).exists()
    assert survey.questions.count() == 2
    for question in survey.questions.all():
        assert SurveyQuestion.objects.filter(
            survey=survey, question=question
        ).exists()
        answer_count = 2 if question.text == 'Question 1' else 1
        assert question.answer_options.count() == answer_count


@pytest.mark.django_db
def test_add_questions_for_survey_with_repo(
    surveys_survey_factory: SurveyFactory,
) -> None:
    """Create add questons for survey with repo method."""
    survey = surveys_survey_factory()
    questions = [
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
                {TEXT: 'Answer 1'},
                {TEXT: 'Answer 2'},
            ],
        },
    ]

    resolve(SurveyRepo).add_questions(survey, questions)
    assert Question.objects.all().count() == 2
    assert AnswerOption.objects.all().count() == 4


@pytest.mark.django_db
def test_add_questions_without_answers(
    surveys_survey_factory: SurveyFactory,
) -> None:
    """Test add_questions without answer options."""
    survey = surveys_survey_factory()
    questions = [
        {
            TEXT: 'Question without answers',
            IS_FAVORITE: False,
            QUESTION_TYPE: SCORE,
            ANSWERS: [],
        }
    ]

    resolve(SurveyRepo).add_questions(survey, questions)

    question = Question.objects.get(text='Question without answers')
    assert question.answer_options.count() == 0
