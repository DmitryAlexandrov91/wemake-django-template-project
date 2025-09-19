from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from server.apps.tgbot.entrypoints import start_handler

if TYPE_CHECKING:
    from tests.plugins.tgbot.fixtures import MockMessage


@pytest.mark.django_db
def test_start_handler_send_message(
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Ensure start handler works correctly."""
    start_handler(message=message_with_user)

    mock_bot_send_message.assert_called_once()
