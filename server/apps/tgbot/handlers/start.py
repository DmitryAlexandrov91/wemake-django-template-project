from __future__ import annotations

import attrs
from telebot import TeleBot, types


@attrs.define(frozen=True)
class StartHandlerService:
    """Start handler service."""

    _bot: TeleBot

    def __call__(self, message: types.Message) -> None:
        """Send Hello message."""
        self._bot.send_message(chat_id=message.chat.id, text='Hello!')
