from __future__ import annotations

import attrs
from telebot import TeleBot, types

from server.apps.tgbot.usecases.survey import (
    HandleSurveyCallbackResponseUseCase,
    HandleSurveyCommandUseCase,
    HandleSurveyMessageResponseUseCase,
)


@attrs.define(frozen=True)
class SurveyHandlerService:
    """Survey handler service."""

    _bot: TeleBot
    _handle_survey_use_case: HandleSurveyCommandUseCase
    _handle_text_response: HandleSurveyMessageResponseUseCase
    _handle_callback_response: HandleSurveyCallbackResponseUseCase

    def __call__(self, message: types.Message) -> None:
        """Begin survey handle logic."""
        self._handle_survey_use_case(message=message)

    def handle_text_answer(self, message: types.Message) -> None:
        """Handle text response for survey answer."""
        self._handle_text_response(message=message)

    def handle_callback_answer(self, call: types.CallbackQuery) -> None:
        """Handle callback response for survey answer."""
        self._handle_callback_response(call=call)
