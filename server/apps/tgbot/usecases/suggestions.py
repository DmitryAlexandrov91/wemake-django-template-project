from dataclasses import dataclass

from telebot import TeleBot, types
from telebot.custom_filters import StateFilter

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.logic.suggestions_usecases import HandleSuggestionUseCase
from server.apps.tgbot.message_templates import (
    EMPTY_SUGGESTION,
    NO_USER,
    NO_USERNAME,
    SUGGESTION_REQUEST,
    SUGGESTION_SAVED,
)
from server.apps.tgbot.states import SuggestState


@dataclass
class HandleSuggestCommandUseCase:
    """Usecase for starting suggestion input."""

    _bot: TeleBot
    _state: StatePostgresStorage

    def __call__(self, message: types.Message) -> None:
        """Ask user to enter their suggestion."""
        if not message.from_user:
            self._bot.send_message(message.chat.id, NO_USER)
            return

        self._bot.add_custom_filter(StateFilter(self._bot))  # type: ignore[no-untyped-call]
        self._state.set_state(
            user_id=message.from_user.id,
            state=SuggestState.waiting_for_suggestion,
            chat_id=message.chat.id,
        )

        self._bot.send_message(
            chat_id=message.chat.id,
            text=SUGGESTION_REQUEST,
        )


@dataclass
class HandleSuggestionTextUseCase:
    """Usecase for completing suggestion input."""

    _bot: TeleBot
    _suggestion_usecase: HandleSuggestionUseCase
    _state: StatePostgresStorage

    def __call__(self, message: types.Message) -> None:
        """Receive suggestion text and save it."""
        if not message.from_user:
            self._bot.send_message(message.chat.id, NO_USER)
            return

        username = message.from_user.username
        if not username:
            self._bot.send_message(message.chat.id, NO_USERNAME)
            return

        if not message.text:
            self._bot.send_message(message.chat.id, EMPTY_SUGGESTION)
            return

        self._suggestion_usecase(
            tg_username=username,
            text=message.text,
        )

        self._state.delete_state(
            user_id=message.from_user.id, chat_id=message.chat.id
        )

        self._bot.send_message(
            chat_id=message.chat.id,
            text=SUGGESTION_SAVED,
        )
