from collections.abc import Callable
from datetime import date, timedelta
from typing import Any, TypedDict, Unpack

import pytest
from django.urls import reverse
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyResult,
    UserAnswer,
)
from server.apps.users.models import CustomUser
from tests.plugins.fakery import FakeryM
from tests.plugins.surveys import QuestionFactory

GET_ALL_SURVEYS_URL = reverse('surveys-list')
CREATE_SURVEY_URL = reverse('surveys-list')

type SurveyFactory = Callable[[Unpack[_SurveyFactoryParams]], Survey]
type SurveyResultFactory = Callable[
    [Unpack[_SurveyResultFactoryParams]], SurveyResult
]
type UserAnswerFactory = Callable[
    [Unpack[_UserAnswerFactoryParams]], UserAnswer
]


class _SurveyFactoryParams(TypedDict, total=False):
    title: str
    description: str
    start_date: date
    end_date: date | None
    department: Department
    is_favorite: bool
    to_delete: bool
    status: str


class _SurveyResultFactoryParams(TypedDict, total=False):
    user: CustomUser
    survey: Survey
    bot_state: str


class _UserAnswerFactoryParams(TypedDict, total=False):
    survey_result: SurveyResult
    question: Question
    text_answer: str
    selected_options: list[AnswerOption]


@pytest.fixture
def surveys_survey_factory(
    fakery_m: FakeryM[Survey],
) -> SurveyFactory:
    """Factory fixture for creating Survey instances."""

    def factory(**kwargs: Unpack[_SurveyFactoryParams]) -> Survey:
        return fakery_m(Survey)(**kwargs)

    return factory


@pytest.fixture
def surveys_survey_result_factory(
    fakery_m: FakeryM[SurveyResult],
) -> SurveyResultFactory:
    """Factory fixture for creating SurveyResult instances."""

    def factory(**kwargs: Unpack[_SurveyResultFactoryParams]) -> SurveyResult:
        return fakery_m(SurveyResult)(**kwargs)

    return factory


@pytest.fixture
def surveys_user_answer_result_factory(
    fakery_m: FakeryM[UserAnswer],
) -> UserAnswerFactory:
    """Factory fixture for creating SurveyResult instances."""

    def factory(**kwargs: Unpack[_UserAnswerFactoryParams]) -> UserAnswer:
        return fakery_m(UserAnswer)(**kwargs)

    return factory


@pytest.fixture
def survey(surveys_survey_factory: SurveyFactory) -> Survey:
    """Return a single Survey instance created."""
    return surveys_survey_factory(
        title='Original Title',
        description='Original Description',
        start_date=date(2025, 10, 15),
        status=SurveyStatus.DRAFT,
    )


@pytest.fixture
def two_surveys(surveys_survey_factory: SurveyFactory) -> list[Survey]:
    """Fixture for two surveys."""
    return [
        surveys_survey_factory(title='Survey 1', description='Desription1'),
        surveys_survey_factory(title='Survey 2', description='Description2'),
    ]


@pytest.fixture
def two_surveys_to_delete(
    surveys_survey_factory: SurveyFactory,
) -> list[Survey]:
    """Fixture for two surveys with to_delete=True."""
    return [
        surveys_survey_factory(
            title='Survey 1', description='Desription1', to_delete=True
        ),
        surveys_survey_factory(
            title='Survey 2', description='Description2', to_delete=True
        ),
    ]


@pytest.fixture
def two_expired_surveys(
    surveys_survey_factory: SurveyFactory,
) -> list[Survey]:
    """Fixture for two expired surveys."""
    now_date = timezone.now().date()
    return [
        surveys_survey_factory(
            title=f'Survey {count}',
            description=f'Desription{count}',
            end_date=now_date - timedelta(days=count),
            status=SurveyStatus.ACTIVE,
        )
        for count in range(1, 3)
    ]


@pytest.fixture
def question(surveys_question_factory: QuestionFactory) -> Any:
    """Create one question."""
    return surveys_question_factory(text='Question1')


@pytest.fixture
def two_questions_to_delete(surveys_question_factory: QuestionFactory) -> Any:
    """Create two questions with to_delete=True."""
    return [
        surveys_question_factory(text='Question1', to_delete=True),
        surveys_question_factory(text='Question2', to_delete=True),
    ]
