from unittest.mock import MagicMock

import pytest

from server.apps.tgbot.entrypoints.menu import (
    handle_archive_answers_for_period,
    handle_start_date,
)
from tests.plugins.tgbot.fixtures import MockCallbackQuery, MockMessage

CHAT_ID_FIELD = 'chat_id'
TEXT_FIELD = 'text'


@pytest.mark.django_db
def test_handle_archive_answers_for_period(
    mock_callback_query: MockCallbackQuery,
    mock_bot_send_message: MagicMock,
    mock_bot_answer_callback_query: MagicMock,
) -> None:
    """Check handling of 'answers for period' callback."""
    handle_archive_answers_for_period(mock_callback_query)
    mock_bot_send_message.assert_called_once()
    args = mock_bot_send_message.call_args.kwargs
    assert args[CHAT_ID_FIELD] == mock_callback_query.message.chat.id
    assert args[TEXT_FIELD] == 'Введите <b>дату начала</b> в формате DD.MM.YYYY'


def test_handle_start_date(
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Check handling of valid start date input."""
    message_with_user.text = '25.10.2025'
    handle_start_date(message_with_user)
    mock_bot_send_message.assert_called_once()
    args = mock_bot_send_message.call_args.kwargs
    assert args[CHAT_ID_FIELD] == message_with_user.chat.id
    assert args[TEXT_FIELD] == (
        'Введите <b>дату окончания</b> в формате DD.MM.YYYY'
    )


@pytest.mark.django_db
def test_handle_start_date_invalid_format(
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Check handling of invalid start date input."""
    message_with_user.text = 'incorrect date'

    handle_start_date(message_with_user)
    mock_bot_send_message.assert_called_once()
    args = mock_bot_send_message.call_args.kwargs
    assert args[CHAT_ID_FIELD] == message_with_user.chat.id
    assert args[TEXT_FIELD] == (
        'Неверный формат. Введите дату в формате <b>DD.MM.YYYY</b>'
    )
