from dataclasses import dataclass

from django.db.models.query import QuerySet
from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import SurveyResult, UserAnswer
from server.apps.tgbot.callbacks import answer_callback, answer_cancel_callback
from server.apps.tgbot.keyboards.edit_keyboard import (
    EditAnswerKeyboard,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    NO_ANSWERS,
    SURVEY_RESULTS_TEMPLATE,
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
            pk=parsed_data['survey_result_id']
        )
        user_answers = self._user_answer_repo.get_answers_by_survey_result(
            survey_result=survey_result
        )

        keyboard = self._keyboard_builder(
            answers=user_answers,
            survey_result_id=survey_result.pk,
            callback=answer_callback,
        )

        self._edit_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            user_answers=user_answers,
            survey_result=survey_result,
            keyboard=keyboard,
        )

    def _edit_message(
        self,
        chat_id: int | str,
        message_id: int | None,
        user_answers: QuerySet[UserAnswer],
        survey_result: SurveyResult,
        keyboard: types.InlineKeyboardMarkup,
    ) -> None:
        """Edit message method."""
        self._bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=SURVEY_RESULTS_TEMPLATE.format(
                survey_title=survey_result.survey.title,
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
            reply_markup=keyboard,
        )
