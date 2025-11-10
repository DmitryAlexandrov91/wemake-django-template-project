from dataclasses import dataclass

from django.core.exceptions import ValidationError
from telebot import TeleBot, types
from telebot.custom_filters import StateFilter

from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.callbacks import answer_callback, answer_cancel_callback
from server.apps.tgbot.keyboards.edit_keyboard import (
    CancelEditAnswerKeyboard,
    EditAnswerKeyboard,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    NO_ANSWERS,
    PROCESS_NEW_ANSWER_TEXT,
    SURVEY_RESULTS_TEMPLATE,
)
from server.apps.tgbot.states import EditState
from server.apps.users.infra.repository import UserRepo

SURVEY_RESULT_ID = 'survey_result_id'


@dataclass
class HandleEditCommandUseCase:
    """Usecase for edit command."""

    _user_repo: UserRepo
    _survey_repo: SurveyRepo
    _survey_res_repo: SurveyResultRepo
    _user_answer_repo: UserAnswerRepo
    _bot: TeleBot
    _keyboard_builder: EditAnswerKeyboard

    def __call__(self, message: types.Message) -> None:
        """Show responses for user survey."""
        tg_user = message.from_user
        if not tg_user or not tg_user.username:
            raise ValidationError('TG user(name) is not recognized.')

        user = self._user_repo.get_by_tg_username(f'@{tg_user.username}')

        survey = self._survey_repo.get_active_survey_for_user(user=user)

        survey_result = self._survey_res_repo.get_or_create_user_survey_res(
            user=user, survey=survey
        )

        user_answers = self._user_answer_repo.get_answers_by_survey_result(
            survey_result=survey_result
        )

        self._bot.send_message(
            chat_id=message.chat.id,
            text=SURVEY_RESULTS_TEMPLATE.format(
                survey_title=survey.title,
                answers=''.join(
                    ANSWER_TEMPLATE.format(
                        question_number=answer.pk,
                        question_text=answer.question,
                        answer_text=answer.text_answer,
                    )
                    for answer in user_answers
                )
                if user_answers
                else NO_ANSWERS,
            ),
            parse_mode='HTML',
            reply_markup=self._keyboard_builder(
                answers=user_answers,
                survey_result_id=survey_result.pk,
                callback=answer_callback,
            ),
        )


@dataclass
class HandleEditResponseUseCase:
    """Usecase for handle edit answer button."""

    _bot: TeleBot
    _keyboard_builder: CancelEditAnswerKeyboard
    _user_answer_repo: UserAnswerRepo

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
        self._bot.add_custom_filter(StateFilter(self._bot))  # type: ignore[no-untyped-call]
        self._bot.set_state(
            call.from_user.id,
            EditState.waiting_for_new_answer,
            call.message.chat.id,
        )

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            call.from_user.id, call.message.chat.id
        ) as state_data:
            state_data['answer_id'] = parsed_data['answer_id']
            state_data[SURVEY_RESULT_ID] = parsed_data[SURVEY_RESULT_ID]
            state_data['callback_id'] = call.message.id

        self._bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=PROCESS_NEW_ANSWER_TEXT,
            reply_markup=keyboard,
        )


@dataclass
class HandleCancelEditResponseUseCase:
    """Usecase for handle cancel edit button."""

    _bot: TeleBot
    _keyboard_builder: EditAnswerKeyboard
    _user_answer_repo: UserAnswerRepo

    def __call__(self, call: types.CallbackQuery) -> None:
        """Cancel button handler."""
        self._bot.answer_callback_query(call.id)

        if call.data is None:
            return

        parsed_data = answer_cancel_callback.factory.parse(call.data)
        survey_result = SurveyResult.objects.get(
            pk=parsed_data[SURVEY_RESULT_ID]
        )
        user_answers = self._user_answer_repo.get_answers_by_survey_result(
            survey_result=survey_result
        )

        keyboard = self._keyboard_builder(
            answers=user_answers,
            survey_result_id=survey_result.pk,
            callback=answer_callback,
        )

        self._bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=SURVEY_RESULTS_TEMPLATE.format(
                survey_title=survey_result.survey.title,
                answers=''.join(
                    ANSWER_TEMPLATE.format(
                        question_number=answer.pk,
                        question_text=answer.question,
                        answer_text=answer.text_answer,
                    )
                    for answer in user_answers
                )
                if user_answers
                else NO_ANSWERS,
            ),
            parse_mode='HTML',
            reply_markup=keyboard,
        )


@dataclass
class HandleProcessEditResponseUseCase:
    """Usecase for process edit response."""

    _bot: TeleBot
    _keyboard_builder: EditAnswerKeyboard
    _user_answer_repo: UserAnswerRepo
    _survey_result_repo: SurveyResultRepo

    def __call__(self, message: types.Message) -> None:
        """Process answer text edit."""
        self._bot.delete_message(chat_id=message.chat.id, message_id=message.id)

        if message.from_user is None or message.text is None:
            return

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            message.from_user.id, message.chat.id
        ) as state_data:
            survey_result = self._survey_result_repo.get_by_pk(
                pk=state_data[SURVEY_RESULT_ID]
            )
            user_answers = self._user_answer_repo.get_answers_by_survey_result(
                survey_result=survey_result
            )

            self._user_answer_repo.edit_user_answer(
                answer_id=state_data['answer_id'], new_text_answer=message.text
            )

            self._bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=state_data['callback_id'],
                text=SURVEY_RESULTS_TEMPLATE.format(
                    survey_title=survey_result.survey.title,
                    answers=''.join(
                        ANSWER_TEMPLATE.format(
                            question_number=answer.pk,
                            question_text=answer.question,
                            answer_text=answer.text_answer,
                        )
                        for answer in user_answers
                    )
                    if user_answers
                    else NO_ANSWERS,
                ),
                parse_mode='HTML',
                reply_markup=self._keyboard_builder(
                    answers=user_answers,
                    survey_result_id=survey_result.pk,
                    callback=answer_callback,
                ),
            )

        self._bot.delete_state(
            user_id=message.from_user.id, chat_id=message.chat.id
        )
