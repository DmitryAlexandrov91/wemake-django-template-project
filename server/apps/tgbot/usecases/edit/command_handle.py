from dataclasses import dataclass

from django.core.exceptions import ValidationError
from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    SurveyRepo,
)
from server.apps.tgbot.callbacks import survey_list_callback
from server.apps.tgbot.keyboards.edit_keyboard import (
    SurveysListKeyboard,
)
from server.apps.tgbot.message_templates import (
    SURVEY_CHOISE,
)
from server.apps.users.infra.repository import UserRepo


@dataclass
class HandleEditCommandUseCase:
    """Usecase for edit command."""

    _user_repo: UserRepo
    _survey_repo: SurveyRepo
    _bot: TeleBot
    _keyboard: SurveysListKeyboard

    def __call__(self, message: types.Message) -> None:
        """Show list of active surveys for edit."""
        tg_user = message.from_user
        if not tg_user or not tg_user.username:
            raise ValidationError('TG user(name) is not recognized.')

        user = self._user_repo.get_by_tg_username(f'@{tg_user.username}')

        surveys = self._survey_repo.get_active_surveys_for_user(user=user)

        self._bot.send_message(
            chat_id=message.chat.id,
            text=SURVEY_CHOISE,
            reply_markup=self._keyboard(
                surveys=surveys,
                user_id=user.pk,
                callback=survey_list_callback,
            ),
        )
