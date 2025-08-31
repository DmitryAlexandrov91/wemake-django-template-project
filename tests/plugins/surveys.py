from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypedDict, Unpack

import pytest

from server.apps.surveys.choices import QuestionType
from server.apps.surveys.models import AnswerOption, Question

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


class _AnswerOptionFactoryParams(TypedDict, total=False):
    """Base params for AnswerOptionFactory."""

    question: Question
    text: str


@pytest.fixture
def surveys_question_factory(fakery_m: FakeryM[Question]) -> QuestionFactory:
    """Factory fixture for creating Question instances."""

    def factory(**kwargs: Unpack[_QuestionFactoryParams]) -> Question:
        return fakery_m(Question)(**kwargs)

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
def surveys_answer_option_factory(
    fakery_m: FakeryM[AnswerOption],
) -> AnswerOptionFactory:
    """Factory fixture for creating AnswerOption instances."""

    def factory(**kwargs: Unpack[_AnswerOptionFactoryParams]) -> AnswerOption:
        return fakery_m(AnswerOption)(**kwargs)

    return factory


@pytest.fixture
def test_answer_option(
    surveys_answer_option_factory: AnswerOptionFactory,
    consent_given_question: Question,
) -> AnswerOption:
    """Fixture that create a single AnswerOption instance."""
    return surveys_answer_option_factory(
        question=consent_given_question,
        text='Test Answer Option',
    )
