from collections.abc import Callable
from datetime import datetime, timedelta

import pytest

from server.apps.surveys.infra.repository import SurveyResultRepo
from server.apps.tgbot.logic.menu.services import generate_view_answers_message
from server.apps.users.infra.repository import UserRepo
from server.di import resolve

type CheckMessage = Callable[[str, datetime], str]


@pytest.fixture
def make_check_message() -> CheckMessage:
    """Fixture factory for user's answers message."""

    def factory(tg_username: str, curren_date: datetime) -> str:
        """Return formatted answers for given user."""
        user = resolve(UserRepo).get_by_tg_username(tg_username)
        return generate_view_answers_message(
            resolve(SurveyResultRepo)
            .get_completed_surveys(user=user)
            .filter(
                started_at__gte=curren_date - timedelta(days=1),
                started_at__lte=curren_date + timedelta(days=1),
            )
        )

    return factory
