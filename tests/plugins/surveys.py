from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypedDict, Unpack

import pytest

from server.apps.surveys.choices import QuestionType
from server.apps.surveys.models import Question

if TYPE_CHECKING:
    from tests.plugins.fakery import FakeryM

type QuestionFactory = Callable[[Unpack[_QuestionFactoryParams]], Question]


class _QuestionFactoryParams(TypedDict, total=False):
    """Base params for QuestionFactory."""

    text: str
    question_type: QuestionType


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
