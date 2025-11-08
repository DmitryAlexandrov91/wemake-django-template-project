from dataclasses import dataclass
from datetime import datetime

from django.db.models import QuerySet
from telebot import TeleBot, types
from telebot.custom_filters import StateFilter

from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.logic.menu.constants import (
    MESSAGE_END_DATE,
    MESSAGE_INVALIDE_PERIOD,
    MESSAGE_NO_ANSWERS_FOR_PERIOD,
    MESSAGE_START_DATE,
    PARSE_MODE,
)
from server.apps.tgbot.logic.menu.services import (
    PeriodBase,
    generate_view_answers_message,
)
from server.apps.tgbot.logic.menu.usecases import GetCompletedSurveyrs
from server.apps.tgbot.states import SurveyPeriodStates


@dataclass
class InitiatePeriodAnswers:
    """Initiate the process to show survey answers for a selected period."""

    _bot: TeleBot

    def __call__(self, call: types.CallbackQuery) -> None:
        """Handle callback and request start date from user."""
        self._bot.answer_callback_query(call.id)

        self._bot.add_custom_filter(StateFilter(self._bot))  # type: ignore[no-untyped-call]

        self._bot.set_state(
            call.from_user.id,
            SurveyPeriodStates.waiting_for_start_date,
            call.message.chat.id,
        )

        self._bot.send_message(
            chat_id=call.message.chat.id,
            text=MESSAGE_START_DATE,
            parse_mode=PARSE_MODE,
        )


@dataclass
class RequestStartDateForPeriod(PeriodBase):
    """Receive start date and transition to waiting for end date."""

    def __call__(self, message: types.Message) -> None:
        """Handle user input for start date and save it."""
        start_date = self._date_processing(message)

        if not (start_date and message.from_user):
            return

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            message.from_user.id,
            message.chat.id,
        ) as state_data:
            state_data['start_date'] = start_date

        self._bot.set_state(
            message.from_user.id,
            SurveyPeriodStates.waiting_for_end_date,
            message.chat.id,
        )

        self._bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_END_DATE,
            parse_mode=PARSE_MODE,
        )


@dataclass
class FinalizePeriodAnswers(PeriodBase):
    """Receive end date and send completed survey results for the period."""

    _get_results: GetCompletedSurveyrs

    def __call__(self, message: types.Message) -> None:
        """Handle user input for end date and send results."""
        end_date = self._date_processing(message)

        if not (end_date and message.from_user and message.from_user.username):
            return

        with self._bot.retrieve_data(  # type: ignore[union-attr]
            message.from_user.id,
            message.chat.id,
        ) as state_data:
            start_date = state_data.get('start_date')

        if not self._validate_period(start_date, end_date):
            self._bot.send_message(
                chat_id=message.chat.id,
                text=MESSAGE_INVALIDE_PERIOD,
            )
            return

        results_survyes = self._get_results(message.from_user.username).filter(
            started_at__gte=start_date,
            started_at__lte=end_date,
        )

        self._send_results(results_survyes, message.chat.id)

        self._bot.delete_state(message.from_user.id, message.chat.id)

    def _validate_period(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> bool:
        """Validates that the end date is not earlier than the start date."""
        return not start_date > end_date

    def _send_results(
        self,
        results_survyes: QuerySet[SurveyResult],
        chat_id: int,
    ) -> None:
        """Sends survey results to the user via a Telegram message."""
        if not results_survyes:  # noqa: WPS504
            self._bot.send_message(
                chat_id=chat_id,
                text=MESSAGE_NO_ANSWERS_FOR_PERIOD,
            )
        else:
            self._bot.send_message(
                chat_id=chat_id,
                text=generate_view_answers_message(results_survyes),
                parse_mode=PARSE_MODE,
            )
