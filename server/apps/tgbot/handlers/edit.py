from __future__ import annotations

import attrs
from telebot import TeleBot, types

from server.apps.tgbot.usecases.edit import (
    HandleCancelEditResponseUseCase,
    HandleEditCommandUseCase,
    HandleEditResponseUseCase,
    HandleProcessEditResponseUseCase,
)


@attrs.define(frozen=True)
class EditHandlerService:
    """Handler for edit responses."""

    _bot: TeleBot
    _handle_edit_use_case: HandleEditCommandUseCase
    _handle_edit_response_use_case: HandleEditResponseUseCase
    _handle_cancel_edit_response_use_case: HandleCancelEditResponseUseCase
    _handle_process_edit_response_use_case: HandleProcessEditResponseUseCase

    def __call__(self, message: types.Message) -> None:
        """Edit command handler."""
        self._handle_edit_use_case(message)

    def enter_new_text(self, call: types.CallbackQuery) -> None:
        """Processing new question text input."""
        self._handle_edit_response_use_case(call=call)

    def cancel(self, call: types.CallbackQuery) -> None:
        """Processing cancel button."""
        self._handle_cancel_edit_response_use_case(call=call)

    def process_new_answer_text(self, message: types.Message) -> None:
        """Processing edit answer text."""
        self._handle_process_edit_response_use_case(message=message)
