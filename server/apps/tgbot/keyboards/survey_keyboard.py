from dataclasses import dataclass

from django.db import models
from telebot import types

from server.apps.surveys.models.surveys import (
    AnswerOption,
    Question,
    SurveyResult,
)
from server.apps.tgbot.callbacks import CallbackFactory
from server.apps.tgbot.services.keyboard_builder import (
    ButtonBuilderService,
    KeyboardBuilderService,
)


@dataclass(frozen=True, slots=True)
class SurveyHandleKeyboard:
    """Service to build keyboard for survey handle."""

    _keyboard_builder: KeyboardBuilderService
    _button_builder: ButtonBuilderService

    def __call__(
        self,
        survey_result: SurveyResult,
        answer_options: models.QuerySet[AnswerOption],
        current_question: Question,
        callback: CallbackFactory,
        row_width: int = 2,
    ) -> types.InlineKeyboardMarkup:
        """KB for choise answer options or waiting user answer."""
        keyboard = self._keyboard_builder(row_width=row_width)
        buttons = []
        for option in answer_options:
            button = self._button_builder(
                text=option.text,
                callback=callback,
                callback_data={
                    'question_id': current_question.pk,
                    'survey_result_id': survey_result.pk,
                    'answer_option': option,
                },
            )
            buttons.append(button)

        keyboard.add(*buttons)
        return keyboard
