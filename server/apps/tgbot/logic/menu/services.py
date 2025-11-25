import re
from dataclasses import dataclass
from datetime import datetime

from django.db.models import QuerySet
from django.utils import timezone
from telebot import TeleBot, types

from server.apps.surveys.models import SurveyResult
from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.logic.menu.constants import (
    DATE_PATTERN,
    MESSAGE_INVALIDE_DATE,
    PARSE_MODE,
)
from server.apps.tgbot.message_templates import (
    ANSWER_TEMPLATE,
    ANSWERS_LIST_TEMPLATE,
)


@dataclass
class PeriodBase:
    """Base class with common date validation and parsing methods."""

    _bot: TeleBot
    _state: StatePostgresStorage

    def _send_invalid_date_format_message(self, chat_id: int) -> None:
        """Send message about invalid date format."""
        self._bot.send_message(
            chat_id=chat_id,
            text=MESSAGE_INVALIDE_DATE,
            parse_mode=PARSE_MODE,
        )

    def _validate_date(self, date: str) -> re.Match[str] | None:
        """Check if the date matches DD.MM.YYYY format."""
        return re.fullmatch(DATE_PATTERN, date)

    def _parse_aware_datetime(self, text: str) -> datetime:
        """Parse string into timezone-aware datetime."""
        return datetime.strptime(text, '%d.%m.%Y').replace(
            tzinfo=timezone.get_current_timezone(),
        )

    def _date_processing(self, message: types.Message) -> datetime | None:
        """Validate and parse the user input date."""
        text = message.text.strip()  # type: ignore[union-attr]

        if self._validate_date(text) is None:
            self._send_invalid_date_format_message(message.chat.id)
            return None

        return self._parse_aware_datetime(text)


def generate_view_answers_message(
    archive_survey: QuerySet[SurveyResult],
) -> str:
    """Generate formatted message with user's answers."""
    results_survey = []

    for archive_results in archive_survey:
        results_survey.append(
            ANSWERS_LIST_TEMPLATE.format(
                survey_title=archive_results.survey.title
            ),
        )
        for index, answer in enumerate(
            archive_results.user_answers.all(), start=1
        ):
            results_survey.append(
                ANSWER_TEMPLATE.format(
                    question_number=index,
                    question_text=answer.question.text,
                    answer_text=answer.text_answer,
                )
            )

    return ''.join(results_survey)
