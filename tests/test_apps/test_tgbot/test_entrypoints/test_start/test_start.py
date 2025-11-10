from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ValidationError

from server.apps.tgbot.entrypoints.start import start_handler

if TYPE_CHECKING:
    from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_start_handler_send_message(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Ensure start handler works correctly."""
    tg_user = user_from_message_with_relations.from_user
    assert tg_user is not None
    assert tg_user.username is not None

    start_handler(message=user_from_message_with_relations)


@pytest.mark.django_db
def test_start_handler_tg_user_none(
    user_from_message_with_relations: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Test ValidationError if no TG user in message."""
    user_from_message_with_relations.from_user = None
    with pytest.raises(ValidationError):
        start_handler(message=user_from_message_with_relations)
