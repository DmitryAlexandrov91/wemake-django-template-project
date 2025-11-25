from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import models
from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    AnswerOptionRepo,
)
from server.apps.surveys.models.surveys import AnswerOption, SurveyResult
from server.apps.tgbot.callbacks import survey_callback
from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.message_templates import (
    SURVEY_COMPLITED,
    SURVEY_CONTINUE,
    TgBotQuestionType,
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
    _state: StatePostgresStorage

    def __call__(self, message: types.Message) -> Any:
        """Handle message text response."""
        self._bot.delete_message(message_id=message.id, chat_id=message.chat.id)

        tg_user = message.from_user
        if tg_user is None or tg_user.username is None or message.text is None:
            return

        updated_survey_result, message_id = (
            self._retrieve_data_and_process_answer(
                user_id=tg_user.id, chat_id=message.chat.id, text=message.text
            )
        )

        answer_options = self._answer_option_repo.get_by_question(
            question=updated_survey_result.current_question
        )

        if updated_survey_result.current_question is None:
            self._state.delete_state(
                user_id=tg_user.id, chat_id=message.chat.id
            )

        self._edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            updated_survey_result=updated_survey_result,
            answer_options=answer_options,
        )

        self._state.set_data(
            user_id=tg_user.id,
            chat_id=message.chat.id,
            key='question_id',
            value=(
                None
                if updated_survey_result.current_question is None
                else updated_survey_result.current_question.pk
            ),
        )

    def _edit_message_text(
        self,
        chat_id: int | str | None,
        message_id: int | None,
        updated_survey_result: SurveyResult,
        answer_options: models.QuerySet[AnswerOption],
    ) -> None:
        """Method for edit message text."""
        self._bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=SURVEY_COMPLITED
            if updated_survey_result.current_question is None
            else SURVEY_CONTINUE.format(
                question=updated_survey_result.current_question,
                question_type=TgBotQuestionType[
                    updated_survey_result.current_question.question_type
                ],
            ),
            reply_markup=None
            if updated_survey_result.current_question is None
            else self._keyboard_builder(
                answer_options=answer_options,
                survey_result=updated_survey_result,
                current_question=updated_survey_result.current_question,
                callback=survey_callback,
            ),
            parse_mode='HTML',
        )

    def _retrieve_data_and_process_answer(
        self, user_id: int, chat_id: int, text: str
    ) -> tuple[SurveyResult, Any]:
        """Retrieve data, process answer and returns objs."""
        with self._state.get_interactive_data(
            user_id=user_id, chat_id=chat_id
        ) as state_data:
            updated_survey_result = self._processing_answer_use_case(
                survey_result_id=state_data['survey_result_id'],
                question_id=state_data['question_id'],
                answer_text=text,
            )
            message_id = state_data['message_id']

            return updated_survey_result, message_id
