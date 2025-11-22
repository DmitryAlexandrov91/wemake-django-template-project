from dataclasses import dataclass

from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
)
from server.apps.tgbot.callbacks import (
    back_to_active_surveys,
    survey_list_callback,
)
from server.apps.tgbot.keyboards.edit_keyboard import (
    SurveysListKeyboard,
)
from server.apps.tgbot.message_templates import (
    SURVEY_CHOISE,
)
from server.apps.users.infra.repository import UserRepo


@dataclass
class HandleBackButtonUseCase:
    """Usecase for back button to edit surveys."""

    _user_repo: UserRepo
    _survey_repo: SurveyRepo
    _bot: TeleBot
    _keyboard: SurveysListKeyboard
    _survey_result_repo: SurveyResultRepo

    def __call__(self, call: types.CallbackQuery) -> None:
        """Show list of active surveys for edit."""
        self._bot.answer_callback_query(callback_query_id=call.id)
        if call.data is None:
            return

        parsed_data = back_to_active_surveys.factory.parse(
            callback_data=call.data
        )

        survey_result = self._survey_result_repo.get_by_pk(
            pk=int(parsed_data['survey_result_id'])
        )

        surveys = self._survey_repo.get_active_surveys_for_user(
            user=survey_result.user
        )

        self._bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=SURVEY_CHOISE,
            reply_markup=self._keyboard(
                surveys=surveys,
                user_id=survey_result.user.pk,
                callback=survey_list_callback,
            ),
        )
