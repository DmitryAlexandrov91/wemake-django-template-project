from dataclasses import dataclass

from django.db.models import QuerySet
from telebot import TeleBot, types
from telebot.util import quick_markup

from server.apps.surveys.infra.repository import SurveyResultRepo
from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.logic.menu.constants import (
    BUTTON_ALL_ARCHIVED_ANSWERS,
    BUTTON_PERIOD_ANSWERS,
    MENU_ACTION_TEXT,
)
from server.apps.users.infra.repository import UserRepo


@dataclass
class SendMenuUseCase:
    """Send main menu with action buttons."""

    _bot: TeleBot

    def __call__(self, message: types.Message) -> None:
        """Send menu markup to user."""
        markup = quick_markup(
            {
                BUTTON_ALL_ARCHIVED_ANSWERS: {
                    'callback_data': 'show_all_archive_answers'
                },
                BUTTON_PERIOD_ANSWERS: {
                    'callback_data': 'show_archive_answers_for_period'
                },
            },
            row_width=2,
        )

        self._bot.send_message(
            chat_id=message.chat.id,
            text=MENU_ACTION_TEXT,
            reply_markup=markup,
        )


@dataclass
class GetCompletedSurveyrs:
    """Use case to get a user's completed survey results."""

    _user_repo: UserRepo
    _survey_res_repo: SurveyResultRepo

    def __call__(
        self,
        username: str,
    ) -> QuerySet[SurveyResult]:
        """Return a QuerySet of the user's completed survey results."""
        user = self._user_repo.get_by_tg_username(
            f'@{username}',
        )
        return self._survey_res_repo.get_completed_surveys(user)
