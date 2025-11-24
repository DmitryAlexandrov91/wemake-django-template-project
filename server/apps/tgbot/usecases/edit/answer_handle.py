from dataclasses import dataclass

from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
)
from server.apps.tgbot.callbacks import answer_callback, answer_cancel_callback
from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.keyboards.edit_keyboard import (
    CancelEditAnswerKeyboard,
)
from server.apps.tgbot.message_templates import (
    PROCESS_NEW_ANSWER_TEXT,
)
from server.apps.tgbot.states import EditState


@dataclass
class HandleEditResponseUseCase:
    """Usecase for handle edit answer button."""

    _bot: TeleBot
    _keyboard_builder: CancelEditAnswerKeyboard
    _user_answer_repo: UserAnswerRepo
    _state: StatePostgresStorage

    def __call__(self, call: types.CallbackQuery) -> None:
        """Enter new text for answer."""
        self._bot.answer_callback_query(call.id)
        if call.data is None:
            return

        parsed_data = answer_callback.factory.parse(call.data)
        keyboard = self._keyboard_builder(
            parsed_data=parsed_data,
            callback=answer_cancel_callback,
        )

        self._state.set_state(
            user_id=call.from_user.id,
            chat_id=call.message.chat.id,
            state=EditState.waiting_for_new_answer,
        )

        with self._state.get_interactive_data(
            user_id=call.from_user.id, chat_id=call.message.chat.id
        ) as state_data:
            state_data['answer_id'] = parsed_data['answer_id']
            state_data['survey_result_id'] = parsed_data['survey_result_id']
            state_data['callback_id'] = call.message.id

        self._bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=PROCESS_NEW_ANSWER_TEXT,
            reply_markup=keyboard,
        )
