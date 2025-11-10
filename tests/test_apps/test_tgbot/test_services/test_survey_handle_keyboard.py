import pytest
from django.db import models
from telebot import types

from server.apps.surveys.models.surveys import (
    AnswerOption,
    Question,
    SurveyResult,
)
from server.apps.tgbot.callbacks import survey_callback
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.di import resolve
from tests.plugins.fakery import FakeryM


@pytest.mark.django_db
def test_survey_handle_keyboard(fakery_m: FakeryM[models.Model]) -> None:
    """Test that SurveyHandleKeyboard work correctly."""
    survey_result = fakery_m(SurveyResult)()
    question = fakery_m(Question)()
    batch = 3
    row_width = 1
    for _ in range(batch):
        fakery_m(AnswerOption)(question=question, text=f'Option #{_}')
    keyboard = resolve(SurveyHandleKeyboard)(
        survey_result=survey_result,  # type: ignore[arg-type]
        answer_options=AnswerOption.objects.filter(question=question),  # type: ignore[misc]
        current_question=question,  # type: ignore[arg-type]
        callback=survey_callback,
        row_width=row_width,
    )

    assert isinstance(keyboard, types.InlineKeyboardMarkup)
    assert keyboard.row_width == row_width
    assert len(keyboard.keyboard) == batch
