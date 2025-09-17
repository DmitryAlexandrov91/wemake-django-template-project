from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypedDict, Unpack

import pytest
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys import choices, models

if TYPE_CHECKING:
    from tests.plugins.fakery import FakeryM

type QuestionFactory = Callable[
    [Unpack[_QuestionFactoryParams]], models.Question
]
type AnswerOptionFactory = Callable[
    [Unpack[_AnswerOptionFactoryParams]], models.AnswerOption
]


class _QuestionFactoryParams(TypedDict, total=False):
    """Base params for QuestionFactory."""

    text: str
    question_type: choices.QuestionType
    survey: models.Survey
    is_favorite: bool


class _AnswerOptionFactoryParams(TypedDict, total=False):
    """Base params for AnswerOptionFactory."""

    question: models.Question
    text: str


@pytest.fixture
def surveys_question_factory(
    fakery_m: FakeryM[models.Question],
) -> QuestionFactory:
    """Factory fixture for creating Question instances."""

    def factory(**kwargs: Unpack[_QuestionFactoryParams]) -> models.Question:
        return fakery_m(models.Question)(**kwargs)

    return factory


@pytest.fixture
def surveys_answer_option_factory(
    fakery_m: FakeryM[models.AnswerOption],
) -> AnswerOptionFactory:
    """Factory fixture for creating AnswerOption instances."""

    def factory(
        **kwargs: Unpack[_AnswerOptionFactoryParams],
    ) -> models.AnswerOption:
        return fakery_m(models.AnswerOption)(**kwargs)

    return factory


@pytest.fixture
def consent_given_question(
    surveys_question_factory: QuestionFactory,
) -> models.Question:
    """Fixture that create a single Question instance."""
    return surveys_question_factory(
        text='Test Question',
        question_type=choices.QuestionType.CONSENT_GIVEN,
    )


@pytest.fixture
def surveys_answer_option_batch(
    surveys_answer_option_factory: AnswerOptionFactory,
    consent_given_question: models.Question,
) -> Callable[[int], list[models.AnswerOption]]:
    """Factory fixture for creating batches of AnswerOption instances."""

    def factory(batch_size: int) -> list[models.AnswerOption]:
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
) -> Callable[[int, bool], list[models.Question]]:
    """Factory fixture for creating batches of Question instances."""

    def factory(
        batch_size: int = 1, *, is_favorite: bool = False
    ) -> list[models.Question]:
        department = Department.objects.create(name='Test Department')
        survey = models.Survey.objects.create(
            title='Test Survey',
            department=department,
            start_date=timezone.now().date(),
        )
        questions = []
        for num in range(batch_size):
            question = surveys_question_factory(
                survey=survey,
                text=f'Question {num}',
                question_type=choices.QuestionType.RATING_SCALE,
                is_favorite=is_favorite,
            )
            questions.append(question)
        return questions

    return factory  # type: ignore[return-value]
