from dataclasses import dataclass

from django.db.models.query import QuerySet
from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import Survey, SurveyResult, UserAnswer
from server.apps.tgbot.callbacks import answer_callback, survey_list_callback
from server.apps.tgbot.keyboards.edit_keyboard import (
    EditAnswerKeyboard,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    NO_ANSWERS,
    SURVEY_RESULTS_TEMPLATE,
)
from server.apps.users.infra.repository import UserRepo


@dataclass
class SurveyAnswersEditUseCase:
    """Usecase for edit answers after choise survey."""

    _bot: TeleBot
    _survey_repo: SurveyRepo
    _user_repo: UserRepo
    _survey_res_repo: SurveyResultRepo
    _user_answer_repo: UserAnswerRepo
    _keyboard: EditAnswerKeyboard

    def __call__(self, call: types.CallbackQuery) -> None:
        """Handle logic after choise survey."""
        self._bot.answer_callback_query(callback_query_id=call.id)
        if call.data is None:
            return

        parsed_data = survey_list_callback.factory.parse(call.data)

        user = self._user_repo.get_by_pk(pk=int(parsed_data['user_id']))
        survey = self._survey_repo.get_by_pk(pk=int(parsed_data['survey_id']))

        survey_result = self._survey_res_repo.get_or_create_user_survey_res(
            user=user, survey=survey
        )

        user_answers = self._user_answer_repo.get_answers_by_survey_result(
            survey_result=survey_result
        )

        self._edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            survey=survey,
            survey_result=survey_result,
            user_answers=user_answers,
        )

    def _edit_message_text(
        self,
        chat_id: int,
        message_id: int | None,
        survey: Survey,
        user_answers: QuerySet[UserAnswer],
        survey_result: SurveyResult,
    ) -> None:
        """Edit message text method."""
        self._bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=SURVEY_RESULTS_TEMPLATE.format(
                survey_title=survey.title,
                end_date=survey.end_date,
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
            reply_markup=self._keyboard(
                answers=user_answers,
                survey_result_id=survey_result.pk,
                callback=answer_callback,
            ),
        )
