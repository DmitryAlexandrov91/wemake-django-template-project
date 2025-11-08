from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

from server.apps.tgbot.entrypoints.menu import handle_end_date
from server.apps.users.models import CustomUser
from tests.plugins.tgbot.fixtures import MockMessage
from tests.plugins.tgbot.menu.bot_state_factory import BotStateFactory
from tests.plugins.tgbot.menu.user_message_factory import CheckMessage

CHAT_ID_FIELD = 'chat_id'
TEXT_FIELD = 'text'


@pytest.mark.django_db
def test_handle_end_date(
    auth_user: CustomUser,
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
    make_bot_state_with_start_date: BotStateFactory,
    make_check_message: CheckMessage,
) -> None:
    """Test handling of a valid end date input."""
    now = datetime.now(tz=timezone.get_current_timezone())
    msg = make_bot_state_with_start_date(
        message=message_with_user,
        user=auth_user,
        start_date=(now - timedelta(days=1)),
    )
    check_message = make_check_message(auth_user.tg_username, now)
    msg.text = (now + timedelta(days=1)).strftime('%d.%m.%Y')
    handle_end_date(msg)

    kwargs = mock_bot_send_message.call_args.kwargs
    assert kwargs[TEXT_FIELD] == check_message


@pytest.mark.parametrize(
    ('text', 'from_user', 'username'),
    [
        ('some text', None, None),
        ('some text', MagicMock(), None),
        ('some text', MagicMock(), ''),
    ],
)
def test_hadke_end_message_none(
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
    text: str | None,
    from_user: MagicMock | None,
    username: str | None,
) -> None:
    """Test early return when text, from_user, or username is missing."""
    message_with_user.text = text
    message_with_user.from_user = from_user
    if message_with_user.from_user is not None and username is not None:
        message_with_user.from_user.username = username

    request_results = handle_end_date(message_with_user)

    assert request_results is None


@pytest.mark.django_db
def test_handle_end_date_invalide_period(
    auth_user: CustomUser,
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
    make_bot_state_with_start_date: BotStateFactory,
) -> None:
    """Test invalid end date before start."""
    now = datetime.now(tz=timezone.get_current_timezone())
    msg = make_bot_state_with_start_date(
        message=message_with_user,
        user=auth_user,
        start_date=(now + timedelta(days=1)),
    )
    msg.text = now.strftime('%d.%m.%Y')
    request_results = handle_end_date(msg)
    assert request_results is None

    kwargs = mock_bot_send_message.call_args.kwargs
    assert kwargs[TEXT_FIELD] == (
        'Дата окончания раньше даты начала. Попробуйте снова.'
    )


@pytest.mark.django_db
def test_handle_end_date_no_results(
    auth_user: CustomUser,
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
    make_bot_state_with_start_date: BotStateFactory,
) -> None:
    """Test end date with no survey results."""
    now = datetime.now(tz=timezone.get_current_timezone())
    msg = make_bot_state_with_start_date(
        message=message_with_user,
        user=auth_user,
        start_date=(now - timedelta(days=3)),
    )
    msg.text = (now - timedelta(days=1)).strftime('%d.%m.%Y')
    handle_end_date(msg)

    kwargs = mock_bot_send_message.call_args.kwargs
    assert kwargs[TEXT_FIELD] == 'Нет ответов за указанный период.'
