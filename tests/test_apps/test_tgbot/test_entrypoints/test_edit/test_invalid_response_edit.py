from unittest.mock import MagicMock

import pytest

from server.apps.tgbot.entrypoints.edit import responses_edit_handler
from server.apps.tgbot.message_templates import (
    SURVEY_NOT_FOUND,
    SURVEY_STATUS_EDIT_FORBIDDEN,
)
from server.apps.users.models import CustomUser
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_invalid_edit_answer(  # noqa: WPS211
    auth_user: CustomUser,
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Test handler when no active survey is found for the user."""
    assert message_with_user.from_user is not None
    message_with_user.from_user.username = auth_user.tg_username.lstrip('@')
    responses_edit_handler(message_with_user)

    mock_bot_send_message.assert_called_once()

    kwargs = mock_bot_send_message.call_args.kwargs
    assert kwargs['text'] == SURVEY_NOT_FOUND


@pytest.mark.django_db
def test_invalid_edit_answer_survey_completed(
    user_msg_rel_survey_completed: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Test edit restriction when survey status is completed."""
    message = user_msg_rel_survey_completed

    responses_edit_handler(message)

    mock_bot_send_message.assert_called_once()
    kwargs = mock_bot_send_message.call_args.kwargs
    assert kwargs['text'] == SURVEY_STATUS_EDIT_FORBIDDEN
