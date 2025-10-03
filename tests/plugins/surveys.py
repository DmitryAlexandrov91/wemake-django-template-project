from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypedDict, Unpack

import pytest
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys.choices import QuestionType
from server.apps.surveys.models import AnswerOption, Question, Survey
from tests.plugins.department_factory import DepartmentFactory
from tests.plugins.surveys_survey import SurveyFactory

if TYPE_CHECKING:
    from tests.plugins.fakery import FakeryM

type QuestionFactory = Callable[[Unpack[_QuestionFactoryParams]], Question]
type AnswerOptionFactory = Callable[
    [Unpack[_AnswerOptionFactoryParams]], AnswerOption
]


class _QuestionFactoryParams(TypedDict, total=False):
    """Base params for QuestionFactory."""

    text: str
    question_type: QuestionType
    surveys: set[Survey]
    is_favorite: bool


class _AnswerOptionFactoryParams(TypedDict, total=False):
    """Base params for AnswerOptionFactory."""

    question: Question
    text: str


@pytest.fixture
def surveys_question_factory(
    fakery_m: FakeryM[Question],
) -> QuestionFactory:
    """Factory fixture for creating Question instances."""

    def factory(
        **kwargs: Unpack[_QuestionFactoryParams],
    ) -> Question:
        return fakery_m(Question)(**kwargs)

    return factory


@pytest.fixture
def surveys_answer_option_factory(
    fakery_m: FakeryM[AnswerOption],
) -> AnswerOptionFactory:
    """Factory fixture for creating AnswerOption instances."""

    def factory(
        **kwargs: Unpack[_AnswerOptionFactoryParams],
    ) -> AnswerOption:
        return fakery_m(AnswerOption)(**kwargs)

    return factory


@pytest.fixture
def consent_given_question(
    surveys_question_factory: QuestionFactory,
) -> Question:
    """Fixture that create a single Question instance."""
    return surveys_question_factory(
        text='Test Question',
        question_type=QuestionType.CONSENT_GIVEN,
    )


@pytest.fixture
def surveys_answer_option_batch(
    surveys_answer_option_factory: AnswerOptionFactory,
    consent_given_question: Question,
) -> Callable[[int], list[AnswerOption]]:
    """Factory fixture for creating batches of AnswerOption instances."""

    def factory(batch_size: int) -> list[AnswerOption]:
        return [
            surveys_answer_option_factory(
                question=consent_given_question,
                text=f'Option {num}',
            )
            for num in range(batch_size)
        ]

    return factory


@pytest.fixture
def questions_batch(
    surveys_question_factory: QuestionFactory,
) -> Callable[[int, bool], list[Question]]:
    """Factory fixture for creating batches of Question instances."""

    def factory(
        batch_size: int = 1, *, is_favorite: bool = False
    ) -> list[Question]:
        department = Department.objects.create(name='Test Department')
        survey = Survey.objects.create(
            title='Test Survey',
            department=department,
            start_date=timezone.now().date(),
        )
        questions = []
        for num in range(batch_size):
            question = surveys_question_factory(
                text=f'Question {num}',
                question_type=QuestionType.RATING_SCALE,
                is_favorite=is_favorite,
            )
            question.surveys.add(survey)
            questions.append(question)
        return questions

    return factory  # type: ignore[return-value]


@pytest.fixture
def survey_with_question(
    surveys_survey_factory: Callable[..., Survey],
    surveys_question_factory: Callable[..., Question],
) -> Callable[[dict[str, Any]], tuple[Survey, Question]]:
    """Fixture for creating a survey with a question."""

    def factory(
        survey_params: dict[str, Any],
    ) -> tuple[Survey, Question]:
        survey = surveys_survey_factory(**survey_params)
        question = surveys_question_factory(text='Question.')
        question.surveys.add(survey)
        return survey, question

    return factory


@pytest.fixture
def create_surveys(
    surveys_survey_factory: SurveyFactory,
    department_factory: DepartmentFactory,
) -> Callable[[Department], Survey]:
    """Fixture for creating all survey types."""

    def factory(department: Department) -> Survey:
        today = timezone.now().date()
        surveys_survey_factory(
            title='Another department survey',
            description='Another survey text',
            start_date=today,
            end_date=today + timedelta(days=30),
            department=department_factory(name='Department1'),
            is_favorite=False,
        )
        active_survey = surveys_survey_factory(
            title='Active survey',
            description='Active survey text',
            start_date=today,
            end_date=today + timedelta(days=30),
            department=department,
            is_favorite=False,
        )
        surveys_survey_factory(
            title='Ended survey',
            description='Ended survey text',
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            department=department,
            is_favorite=False,
        )
        return active_survey

    return factory


@pytest.fixture
def question_with_two_surveys(  # noqa: WPS234
    surveys_question_factory: Callable[..., Question],
    two_surveys: list[Survey],
) -> Callable[[dict[str, Any]], tuple[Question, list[Survey]]]:  # noqa: WPS221
    """Fixture for creating a question with two surveys."""

    def factory(
        question_params: dict[str, Any] | None = None,
    ) -> tuple[Question, list[Survey]]:
        params_data = question_params or {}
        question = surveys_question_factory(**params_data)
        question.surveys.set(two_surveys)
        return question, two_surveys

    return factory
