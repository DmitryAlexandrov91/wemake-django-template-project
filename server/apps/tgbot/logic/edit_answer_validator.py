from dataclasses import dataclass

from telebot import TeleBot

from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.models.surveys import Survey
from server.apps.tgbot.message_templates import (
    SURVEY_STATUS_EDIT_FORBIDDEN,
)


@dataclass
class ValidatorAnswersUpdatesUseCase:
    """Validate if survey answers can be edited."""

    _bot: TeleBot

    def __call__(self, survey: Survey, chat_id: int) -> bool:
        """Return True if editing allowed, else send message and False."""
        if survey.status in {
            SurveyStatus.COMPLETED,
            SurveyStatus.ARCHIVED,
        }:
            self._bot.send_message(
                chat_id=chat_id, text=SURVEY_STATUS_EDIT_FORBIDDEN
            )
            return False

        return True
