from __future__ import annotations

import attrs
from telebot import TeleBot, types

from server.apps.tgbot.logic.usecases import HandleStartCommandUseCase


@attrs.define(frozen=True)
class StartHandlerService:
    """Start handler service."""

    _bot: TeleBot
    _handle_start_use_case: HandleStartCommandUseCase

    def __call__(self, message: types.Message) -> None:
        """Send Hello message."""
        self._handle_start_use_case.execute(message)
        self._bot.send_message(chat_id=message.chat.id, text='Hello!')
