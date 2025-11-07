from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    AnswerOptionRepo,
    QuestionRepo,
    SurveyResultRepo,
)
from server.apps.surveys.usecases.advance_to_next_question import (
    AdvanceToNextQuestion,
)
from server.apps.tgbot.callbacks import survey_callback
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.message_templates import (
    SURVEY_COMPLITED,
    SURVEY_CONTINUE,
)
from server.apps.tgbot.usecases.common import SaveAnswerUseCase


@dataclass
class HandleSurveyCallbackResponseUseCase:
    """Usecase to handle callback response for survey answer."""

    _bot: TeleBot
    _question_repo: QuestionRepo
    _survey_result_repo: SurveyResultRepo
    _save_answer_use_case: SaveAnswerUseCase
    _advance_to_next_question: AdvanceToNextQuestion
    _answer_option_repo: AnswerOptionRepo
    _keyboard_builder: SurveyHandleKeyboard

    def __call__(self, call: types.CallbackQuery) -> Any:
        """Handle callback response."""
        self._bot.answer_callback_query(call.id)

        if call.data is None:
            return

        parsed_data = survey_callback.factory.parse(call.data)
        survey_result = self._survey_result_repo.get_by_pk(
            pk=parsed_data['survey_result_id']
        )
        question = self._question_repo.get_by_pk(pk=parsed_data['question_id'])
        self._save_answer_use_case(
            survey_result=survey_result,
            question=question,
            answer_text=parsed_data['answer_option'],
        )
        updated_survey_result = self._advance_to_next_question(
            survey_result=survey_result
        )

        answer_options = self._answer_option_repo.get_by_question(
            question=updated_survey_result.current_question
        )

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            call.from_user.id, call.message.chat.id
        ) as state_data:
            state_data['question_id'] = (
                updated_survey_result.current_question.pk
            )

        self._bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=SURVEY_CONTINUE.format(
                question=updated_survey_result.current_question
            )
            if updated_survey_result.current_question
            else SURVEY_COMPLITED,
            reply_markup=self._keyboard_builder(
                answer_options=answer_options,
                survey_result=updated_survey_result,
                current_question=updated_survey_result.current_question,
                callback=survey_callback,
            ),
            parse_mode='HTML',
        )
