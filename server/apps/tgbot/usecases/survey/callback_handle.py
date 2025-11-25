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
class HandleSurveyCallbackResponseUseCase:
    """Usecase to handle callback response for survey answer."""

    _bot: TeleBot
    _answer_option_repo: AnswerOptionRepo
    _keyboard_builder: SurveyHandleKeyboard
    _processing_answer_use_case: ProcessingAnswerUseCase
    _state: StatePostgresStorage

    def __call__(self, call: types.CallbackQuery) -> Any:
        """Handle callback response."""
        self._bot.answer_callback_query(call.id)

        if call.data is None:
            return

        updated_survey_result = self._parse_data_and_process_answer(
            call_data=call.data
        )

        answer_options = self._answer_option_repo.get_by_question(
            question=updated_survey_result.current_question
        )

        self._state.set_data(
            user_id=call.from_user.id,
            chat_id=call.message.chat.id,
            key='question_id',
            value=updated_survey_result.current_question.pk,  # type: ignore[union-attr]
        )

        self._edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            updated_survey_result=updated_survey_result,
            answer_options=answer_options,
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

    def _parse_data_and_process_answer(self, call_data: str) -> SurveyResult:
        """Parce data from call, process answer and returns SurveyResult."""
        parsed_data = survey_callback.factory.parse(call_data)

        return self._processing_answer_use_case(
            survey_result_id=int(parsed_data['survey_result_id']),
            question_id=int(parsed_data['question_id']),
            answer_text=parsed_data['answer_option'],
        )
