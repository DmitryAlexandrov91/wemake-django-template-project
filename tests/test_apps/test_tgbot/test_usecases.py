import pytest
from django.db import models

from server.apps.surveys.models.surveys import (
    AnswerOption,
    Question,
    SurveyResult,
)
from server.apps.tgbot.usecases import SaveAnswerUseCase
from server.di import resolve
from tests.plugins.fakery import FakeryM
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_save_answer_usecase(
    message_with_user: MockMessage, fakery_m: FakeryM[models.Model]
) -> None:
    """Test save answer usercase."""
    message_with_user.text = 'Answer for question'
    answer_option_batch = 3
    survey_result = fakery_m(SurveyResult)()
    question = fakery_m(Question)()

    answer_options = [
        fakery_m(AnswerOption)() for _ in range(answer_option_batch)
    ]

    resolve(SaveAnswerUseCase)(
        survey_result=survey_result,  # type: ignore[arg-type]
        question=question,  # type: ignore[arg-type]
        answer_text=message_with_user.text,  # type: ignore[arg-type]
        selected_options=answer_options,  # type: ignore[arg-type]
    )

    survey_result = SurveyResult.objects.get(pk=survey_result.pk)
    created_user_answer = survey_result.user_answers.get(
        text_answer=message_with_user.text
    )
    assert (
        len(created_user_answer.selected_options.all()) == answer_option_batch
    )


@pytest.mark.django_db
def test_save_answer_without_answer_options(
    message_with_user: MockMessage, fakery_m: FakeryM[models.Model]
) -> None:
    """Test save answer usercase without answer options."""
    message_with_user.text = 'Answer for question'
    survey_result = fakery_m(SurveyResult)()
    question = fakery_m(Question)()

    resolve(SaveAnswerUseCase)(
        survey_result=survey_result,  # type: ignore[arg-type]
        question=question,  # type: ignore[arg-type]
        answer_text=message_with_user.text,  # type: ignore[arg-type]
    )

    survey_result = SurveyResult.objects.get(pk=survey_result.pk)
    created_user_answer = survey_result.user_answers.get(
        text_answer=message_with_user.text
    )
    assert not created_user_answer.selected_options.all()
