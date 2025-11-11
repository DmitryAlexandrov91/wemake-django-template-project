from dataclasses import dataclass

from telebot import TeleBot, types

from server.apps.tgbot.logic.suggestions_usecases import HandleSuggestionUseCase
from server.apps.tgbot.message_templates import (
    NO_TEXT,
    NO_USER,
    NO_USERNAME,
    SUGGESTION_SAVED,
)


@dataclass(frozen=True)
class SuggestionsHandlerService:
    """Service for handling suggestion commands from Telegram bot."""

    _bot: TeleBot
    _use_case: HandleSuggestionUseCase

    def __call__(self, message: types.Message) -> None:
        """Handle incoming suggestion message from user.

        Args:
            message: Telegram message object with suggestion text.
        """
        if not message.from_user:
            self._bot.send_message(
                chat_id=message.chat.id,
                text=NO_USER,
            )
            return

        username = message.from_user.username

        if not username:
            self._bot.send_message(
                chat_id=message.chat.id,
                text=NO_USERNAME,
            )
            return

        if not message.text:
            self._bot.send_message(
                chat_id=message.chat.id,
                text=NO_TEXT,
            )
            return

        self._use_case(tg_username=username, text=message.text)

        self._bot.send_message(
            chat_id=message.chat.id,
            text=SUGGESTION_SAVED,
        )
