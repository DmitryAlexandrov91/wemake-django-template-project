from dataclasses import dataclass

from telebot import TeleBot, types

from server.apps.tgbot.logic.menu.constants import (
    MESSAGE_NO_ANSWER,
    PARSE_MODE,
)
from server.apps.tgbot.logic.menu.services import generate_view_answers_message
from server.apps.tgbot.logic.menu.usecases import GetCompletedSurveyrs


@dataclass
class ShowAllArchiveAnswers:
    """Fetch and show all archived survey answers."""

    _bot: TeleBot
    _get_result: GetCompletedSurveyrs

    def __call__(self, call: types.CallbackQuery) -> None:
        """Handle callback and send all survey answers for the user."""
        self._bot.answer_callback_query(call.id)
        current_answer = self._get_result(call.from_user.username)  # type: ignore[arg-type]
        if current_answer:
            text = generate_view_answers_message(current_answer)
        else:
            text = MESSAGE_NO_ANSWER
        self._bot.send_message(
            chat_id=call.message.chat.id,
            text=text,
            parse_mode=PARSE_MODE,
        )
