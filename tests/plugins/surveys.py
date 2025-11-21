from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypedDict, Unpack

import pytest
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys.choices import QuestionType, SurveyStatus
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
)
from tests.plugins.users_requests import RequestMock

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
    to_delete: bool


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
def survey_activation_request() -> RequestMock:
    """Patch request to change survey status to active."""
    return RequestMock(data={'status': SurveyStatus.ACTIVE})
