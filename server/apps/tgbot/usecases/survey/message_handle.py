from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    AnswerOptionRepo,
)
from server.apps.tgbot.callbacks import survey_callback
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.message_templates import (
    SURVEY_COMPLITED,
    SURVEY_CONTINUE,
)
from server.apps.tgbot.usecases.common import (
    ProcessingAnswerUseCase,
)


@dataclass
class HandleSurveyMessageResponseUseCase:
    """Usecase to handle text response for survey answer."""

    _bot: TeleBot
    _answer_option_repo: AnswerOptionRepo
    _keyboard_builder: SurveyHandleKeyboard
    _processing_answer_use_case: ProcessingAnswerUseCase

    def __call__(self, message: types.Message) -> Any:
        """Handle message text response."""
        self._bot.delete_message(message_id=message.id, chat_id=message.chat.id)

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            message.from_user.id, message.chat.id
        ) as state_data:
            updated_survey_result = self._processing_answer_use_case(
                survey_result_id=state_data['survey_result_id'],
                question_id=state_data['question_id'],
                answer_option=message.text,
            )

            message_id = state_data['message_id']

        answer_options = self._answer_option_repo.get_by_question(
            question=updated_survey_result.current_question
        )

        if updated_survey_result.current_question is None:
            self._bot.delete_state(
                user_id=message.from_user.id, chat_id=message.chat.id
            )

        self._bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text=SURVEY_COMPLITED
            if updated_survey_result.current_question is None
            else SURVEY_CONTINUE.format(
                question=updated_survey_result.current_question
            ),
            reply_markup=self._keyboard_builder(
                answer_options=answer_options,
                survey_result=updated_survey_result,
                current_question=updated_survey_result.current_question,
                callback=survey_callback,
            ),
            parse_mode='HTML',
        )

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            message.from_user.id, message.chat.id
        ) as state_data:
            state_data['question_id'] = (
                updated_survey_result.current_question.pk
            )
