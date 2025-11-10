from collections.abc import Callable
from datetime import datetime
from typing import TypedDict, Unpack

import pytest
from telebot import TeleBot

from server.apps.surveys.choices import SurveyBotState
from server.apps.tgbot.states import SurveyPeriodStates
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import SurveyResultFactory
from tests.plugins.tgbot.fixtures import MockMessage

type BotStateFactory = Callable[[Unpack[_BotState]], MockMessage]


class _BotState(TypedDict, total=False):
    message: MockMessage
    user: CustomUser
    start_date: datetime


@pytest.fixture
def make_bot_state_with_start_date(
    surveys_survey_result_factory: SurveyResultFactory,
) -> BotStateFactory:
    """Factory fixture to set a user's bot start date state."""

    def factory(**kwargs: Unpack[_BotState]) -> MockMessage:
        """Factory to set bot state with start_date for a user message."""
        message: MockMessage = kwargs['message']
        user: CustomUser = kwargs['user']
        start_date: datetime = kwargs['start_date']
        message.from_user.username = user.tg_username.lstrip('@')  # type: ignore[union-attr]
        bot = resolve(TeleBot)
        bot.set_state(
            user_id=message.from_user.id,  # type: ignore[union-attr]
            chat_id=message.chat.id,
            state=SurveyPeriodStates.waiting_for_end_date,
        )
        with bot.retrieve_data(
            user_id=message.from_user.id,  # type: ignore[union-attr]
            chat_id=message.chat.id,
        ) as state_data:
            state_data['start_date'] = start_date

        surveys_survey_result_factory(
            user=user,
            bot_state=SurveyBotState.COMPLETED,
        )

        return message

    return factory
