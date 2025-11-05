from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.core.exceptions import ValidationError
from telebot import TeleBot, types
from telebot.custom_filters import StateFilter

from server.apps.surveys.infra.repository import (
    AnswerOptionRepo,
    QuestionRepo,
    SurveyRepo,
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.callbacks import survey_callback
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.message_templates import SURVEY_START
from server.apps.tgbot.states import SurveyResponseState
from server.apps.users.infra.repository import UserRepo


@dataclass
class HandleSurveyCommandUseCase:
    """Usecase for survey command."""

    _bot: TeleBot
    _user_repo: UserRepo
    _survey_repo: SurveyRepo
    _survey_res_repo: SurveyResultRepo
    _user_answer_repo: UserAnswerRepo
    _question_repo: QuestionRepo
    _answer_option_repo: AnswerOptionRepo
    _keyboard_builder: SurveyHandleKeyboard

    def __call__(self, message: types.Message) -> Any:
        """Start survey handle with current question."""
        tg_user = message.from_user
        if not tg_user or not tg_user.username:
            raise ValidationError('TG user(name) is not recognized.')

        user = self._user_repo.get_by_tg_username(f'@{tg_user.username}')
        active_survey = self._survey_repo.get_active_survey_for_user(user=user)
        survey_result = self._survey_res_repo.get_or_create_user_survey_res(
            user=user, survey=active_survey
        )

        answer_options = self._answer_option_repo.get_by_question(
            question=survey_result.current_question
        )

        if survey_result.current_question is not None:
            self._bot.add_custom_filter(StateFilter(self._bot))  # type: ignore[no-untyped-call]
            self._bot.set_state(
                message.from_user.id,
                SurveyResponseState.survey_response,
                message.chat.id,
            )

            with self._bot.retrieve_data(  # type: ignore[union-attr]
                message.from_user.id, message.chat.id
            ) as state_data:
                state_data['question_id'] = survey_result.current_question.pk
                state_data['survey_result_id'] = survey_result.pk
                state_data['user_id'] = user.pk

        self._bot.send_message(
            chat_id=message.chat.id,
            text=SURVEY_START.format(
                full_name=user.full_name,
                question=survey_result.current_question,
            ),
            parse_mode='HTML',
            reply_markup=self._keyboard_builder(
                answer_options=answer_options,
                survey_result=survey_result,
                current_question=survey_result.current_question,
                callback=survey_callback,
            ),
        )


@dataclass
class HandleSurveyMessageResponseUseCase:
    """Usecase to handle text response for survey answer."""

    _bot: TeleBot

    def __call__(self, message: types.Message) -> Any:
        """Handle message text response."""
        self._bot.delete_message(message_id=message.id, chat_id=message.chat.id)

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            message.from_user.id, message.chat.id
        ) as state_data:
            print(state_data)

        self._bot.delete_state(
            user_id=message.from_user.id, chat_id=message.chat.id
        )


@dataclass
class HandleSurveyCallbackResponseUseCase:
    """Usecase to handle callback response for survey answer."""

    _bot: TeleBot

    def __call__(self, call: types.CallbackQuery) -> Any:
        """Handle callback response."""
        self._bot.answer_callback_query(call.id)

        if call.data is None:
            return

        parsed_data = survey_callback.factory.parse(call.data)
        survey_result = SurveyResult.objects.get(
            pk=parsed_data['survey_result_id']
        )
        print(survey_result)
        print(parsed_data)
