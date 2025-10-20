from dataclasses import dataclass

import telebot


@dataclass
class TelegramService:
    """Kiq data to bot from request body service."""

    _bot: telebot.TeleBot

    def process_update(self, request_body: bytes) -> None:
        """Deserialize data and transfer it to bot."""
        update = telebot.types.Update.de_json(request_body.decode('utf-8'))  # type: ignore[no-untyped-call]
        self._bot.process_new_updates([update])
