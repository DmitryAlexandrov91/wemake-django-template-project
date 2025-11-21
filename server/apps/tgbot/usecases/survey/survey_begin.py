from dataclasses import dataclass

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
from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.message_templates import (
    SURVEY_COMPLITED,
    SURVEY_START,
)
from server.apps.tgbot.states import SurveyResponseState
from server.apps.users.infra.repository import UserRepo
from server.apps.users.models import CustomUser


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
    _state: StatePostgresStorage

    def __call__(
        self, message: types.Message, survey_result: SurveyResult
    ) -> None:
        """Start survey handle with current question."""
        tg_user = message.from_user
        if tg_user is None or message.text is None:
            return

        self._configure_state(user_id=tg_user.id, chat_id=message.chat.id)

        if survey_result.current_question is None:
            self._state.delete_state(
                user_id=tg_user.id, chat_id=message.chat.id
            )

        sent_message = self._send_and_return_message(
            chat_id=message.chat.id,
            survey_result=survey_result,
            full_name=survey_result.user.full_name,
        )

        self._retrieve_data(
            user_id=tg_user.id,
            chat_id=message.chat.id,
            survey_result=survey_result,
            user=survey_result.user,
            sent_message=sent_message,
        )

    def _configure_state(self, user_id: int, chat_id: int) -> None:
        """Add custom filter and set state."""
        self._bot.add_custom_filter(StateFilter(self._bot))  # type: ignore[no-untyped-call]
        self._state.set_state(
            chat_id=chat_id,
            user_id=user_id,
            state=SurveyResponseState.survey_response,
        )

    def _send_and_return_message(
        self, chat_id: int | str, survey_result: SurveyResult, full_name: str
    ) -> types.Message:
        """Send and returns Message."""
        return self._bot.send_message(
            chat_id=chat_id,
            text=SURVEY_COMPLITED
            if survey_result.current_question is None
            else SURVEY_START.format(
                full_name=full_name,
                question=survey_result.current_question,
            ),
            parse_mode='HTML',
            reply_markup=None
            if survey_result.current_question is None
            else self._keyboard_builder(
                answer_options=self._answer_option_repo.get_by_question(
                    question=survey_result.current_question
                ),
                survey_result=survey_result,
                current_question=survey_result.current_question,
                callback=survey_callback,
            ),
        )

    def _retrieve_data(
        self,
        user_id: int,
        chat_id: int,
        survey_result: SurveyResult,
        user: CustomUser,
        sent_message: types.Message,
    ) -> None:
        """Retrieve data after processing is complete."""
        with self._state.get_interactive_data(
            user_id=user_id, chat_id=chat_id
        ) as state_data:
            question_id = (
                None
                if survey_result.current_question is None
                else survey_result.current_question.pk
            )
            state_data['question_id'] = question_id
            state_data['survey_result_id'] = survey_result.pk
            state_data['user_id'] = user.pk
            state_data['message_id'] = sent_message.message_id
