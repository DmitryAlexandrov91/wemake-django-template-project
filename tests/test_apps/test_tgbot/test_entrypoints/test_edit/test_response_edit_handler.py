from unittest.mock import ANY, MagicMock

import pytest
from django.core.exceptions import ValidationError

from server.apps.tgbot.entrypoints.edit import (
    responses_edit_handler,
)
from server.apps.tgbot.message_templates import SURVEY_CHOISE
from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_responses_edit_handler(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Ensure responses_edit_handler works correctly."""
    tg_user = user_from_message_with_relations.from_user
    assert tg_user is not None

    responses_edit_handler(message=user_from_message_with_relations)

    mock_bot_send_message.assert_called_once_with(
        chat_id=user_from_message_with_relations.chat.id,
        text=SURVEY_CHOISE,
        reply_markup=ANY,
    )


@pytest.mark.django_db
def test_responses_edit_handler_with_none_user(
    user_from_message_with_relations: MockMessage,
) -> None:
    """Ensure responses_edit_handler raise ValidationError with None user."""
    user_from_message_with_relations.from_user = None

    with pytest.raises(ValidationError):
        responses_edit_handler(message=user_from_message_with_relations)
