from dataclasses import dataclass

from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.tgbot.callbacks import answer_callback
from server.apps.tgbot.keyboards.edit_keyboard import (
    EditAnswerKeyboard,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    NO_ANSWERS,
    SURVEY_RESULTS_TEMPLATE,
)

SURVEY_RESULT_ID = 'survey_result_id'


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
                            question_number=idx,
                            question_text=answer.question,
                            answer_text=answer.text_answer,
                        )
                        for idx, answer in enumerate(
                            iterable=user_answers, start=1
                        )
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
