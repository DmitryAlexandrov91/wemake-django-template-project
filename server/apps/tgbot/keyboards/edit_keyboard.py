from dataclasses import dataclass
from typing import Any

from django.db import models
from telebot import types

from server.apps.surveys.models.surveys import UserAnswer
from server.apps.tgbot.callbacks import CallbackFactory
from server.apps.tgbot.message_templates import CANSEL_EDIT, EDIT_ANSWER_TEXT
from server.apps.tgbot.services.keyboard_builder import (
    ButtonBuilderService,
    KeyboardBuilderService,
)


@dataclass(frozen=True, slots=True)
class EditAnswerKeyboard:
    """Service to build keyboard fot edit answers."""

    _keyboard_builder: KeyboardBuilderService
    _button_builder: ButtonBuilderService

    def __call__(
        self,
        answers: models.QuerySet[UserAnswer],
        survey_result_id: int,
        callback: CallbackFactory,
        row_width: int = 1,
    ) -> types.InlineKeyboardMarkup:
        """KB for edit UserAnswers."""
        keyboard = self._keyboard_builder(row_width=row_width)
        buttons = []
        for idx, answer in enumerate(iterable=answers, start=1):
            button = self._button_builder(
                text=EDIT_ANSWER_TEXT.format(answer_number=idx),
                callback=callback,
                callback_data={
                    'answer_id': answer.pk,
                    'survey_result_id': survey_result_id,
                },
            )
            buttons.append(button)

        keyboard.add(*buttons)
        return keyboard


@dataclass(frozen=True, slots=True)
class CancelEditAnswerKeyboard:
    """Service to build cancel edit keyboard."""

    _keyboard_builder: KeyboardBuilderService
    _button_builder: ButtonBuilderService

    def __call__(
        self,
        parsed_data: dict[str, Any],
        callback: CallbackFactory,
        row_width: int = 1,
    ) -> types.InlineKeyboardMarkup:
        """Keyboard for cancel edit answer."""
        keyboard = self._keyboard_builder(row_width=row_width)

        keyboard.add(
            self._button_builder(
                text=CANSEL_EDIT,
                callback_data={
                    'answer_id': parsed_data['answer_id'],
                    'survey_result_id': parsed_data['survey_result_id'],
                },
                callback=callback,
            ),
        )

        return keyboard
