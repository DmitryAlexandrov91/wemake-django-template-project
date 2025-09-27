from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from server.apps.surveys import models
from server.apps.tgbot.entrypoints import start_handler
from tests.plugins import department_factory, users

if TYPE_CHECKING:
    from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_start_handler_send_message(
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
    user_factory: users.UserFactory,
    department_factory: department_factory.DepartmentFactory,
    survey_with_question: Callable[
        [dict[str, Any]], tuple[models.Survey, models.Question]
    ],
) -> None:
    """Ensure start handler works correctly."""
    tg_user = message_with_user.from_user
    assert tg_user is not None
    assert tg_user.username is not None
    today = timezone.now().date()
    department = department_factory(name='Department2')
    user_factory(
        username='User1',
        email='user1@mail.com',
        is_active=True,
        is_staff=False,
        tg_username=tg_user.username,
        department=department,
    )
    survey_params = {
        'title': 'Active survey',
        'description': 'Active survey text',
        'start_date': today,
        'end_date': today + timedelta(days=30),
        'department': department,
        'is_favorite': False,
    }
    survey_with_question(survey_params)
    start_handler(message=message_with_user)
    mock_bot_send_message.assert_called_once_with(
        chat_id=message_with_user.chat.id, text='Hello!'
    )


@pytest.mark.django_db
def test_start_handler_tg_user_none(
    message_with_user: MockMessage,
    department_factory: department_factory.DepartmentFactory,
    survey_with_question: Callable[
        [dict[str, Any]], tuple[models.Survey, models.Question]
    ],
) -> None:
    """Test ValidationError if no TG user in message."""
    today = timezone.now().date()
    message_with_user.from_user = None
    department = department_factory(name='Department2')
    survey_params = {
        'title': 'Active survey',
        'description': 'Active survey text',
        'start_date': today,
        'end_date': today + timedelta(days=30),
        'department': department,
        'is_favorite': False,
    }
    survey_with_question(survey_params)
    with pytest.raises(ValidationError):
        start_handler(message=message_with_user)
