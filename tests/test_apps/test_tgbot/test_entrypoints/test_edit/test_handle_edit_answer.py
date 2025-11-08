from unittest.mock import ANY, MagicMock

import pytest

from server.apps.tgbot.callbacks import answer_callback
from server.apps.tgbot.entrypoints.edit_answers import (
    handle_edit_answer,
)
from server.apps.tgbot.message_templates import (
    PROCESS_NEW_ANSWER_TEXT,
)
from tests.plugins.tgbot.fixtures import MockCallbackQuery


@pytest.mark.django_db
def test_handle_edit_answer(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure that handle_edit_answer works correctly."""
    mock_callback_query.data = answer_callback.factory.new(
        answer_id=1, survey_result_id=1
    )
    handle_edit_answer(call=mock_callback_query)
    mock_bot_answer_callback_query.assert_called_once_with(
        mock_callback_query.id
    )
    mock_bot_edit_message_text.assert_called_once_with(
        chat_id=mock_callback_query.message.chat.id,
        message_id=mock_callback_query.message.message_id,
        text=PROCESS_NEW_ANSWER_TEXT,
        reply_markup=ANY,
    )


def test_handle_edit_answer_with_none_data(
    mock_callback_query: MockCallbackQuery,
    mock_bot_answer_callback_query: MagicMock,
    mock_bot_edit_message_text: MagicMock,
) -> None:
    """Ensure handle_edit_answer do nothing without call.data."""
    mock_callback_query.data = None
    handle_edit_answer(call=mock_callback_query)
    mock_bot_edit_message_text.assert_not_called()
