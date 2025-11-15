from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import Survey, SurveyResult, UserAnswer
from server.apps.tgbot.callbacks import answer_callback
from server.apps.tgbot.keyboards.edit_keyboard import (
    EditAnswerKeyboard,
)
from server.apps.tgbot.logic.edit_answer_validator import (
    ValidatorAnswersUpdatesUseCase,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    NO_ANSWERS,
    SURVEY_NOT_FOUND,
    SURVEY_RESULTS_TEMPLATE,
)
from server.apps.users.infra.repository import UserRepo


@dataclass
class HandleEditCommandUseCase:
    """Usecase for edit command."""

    _user_repo: UserRepo
    _survey_repo: SurveyRepo
    _survey_res_repo: SurveyResultRepo
    _user_answer_repo: UserAnswerRepo
    _bot: TeleBot
    _keyboard_builder: EditAnswerKeyboard
    _validator: ValidatorAnswersUpdatesUseCase

    def __call__(self, message: types.Message) -> None:
        """Show responses for user survey."""
        tg_user = message.from_user
        if not tg_user or not tg_user.username:
            raise ValidationError('TG user(name) is not recognized.')

        user = self._user_repo.get_by_tg_username(f'@{tg_user.username}')

        try:
            survey = self._survey_repo.get_active_survey_for_user(user=user)
        except Survey.DoesNotExist:
            self._bot.send_message(
                chat_id=message.chat.id,
                text=SURVEY_NOT_FOUND,
            )
            return

        if not self._validator(survey, message.chat.id):
            return

        survey_result = self._survey_res_repo.get_or_create_user_survey_res(
            user=user, survey=survey
        )
        user_answers = self._user_answer_repo.get_answers_by_survey_result(
            survey_result=survey_result
        )
        self._send_message(
            chat_id=message.chat.id,
            survey=survey,
            user_answers=user_answers,
            survey_result=survey_result,
        )

    def _send_message(
        self,
        chat_id: int | str,
        survey: Survey,
        user_answers: QuerySet[UserAnswer],
        survey_result: SurveyResult,
    ) -> None:
        """Method for send message."""
        self._bot.send_message(
            chat_id=chat_id,
            text=SURVEY_RESULTS_TEMPLATE.format(
                survey_title=survey.title,
                answers=''.join(
                    ANSWER_TEMPLATE.format(
                        question_number=idx,
                        question_text=answer.question,
                        answer_text=answer.text_answer,
                    )
                    for idx, answer in enumerate(iterable=user_answers, start=1)
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
