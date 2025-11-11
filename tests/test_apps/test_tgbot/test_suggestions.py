from unittest.mock import Mock

import pytest

from server.apps.tgbot.constants import SUGGEST_COMMAND
from server.apps.tgbot.handlers.suggestions import SuggestionsHandlerService
from server.apps.tgbot.message_templates import (
    NO_TEXT,
    NO_USER,
    NO_USERNAME,
    SUGGESTION_SAVED,
)
from tests.plugins.tgbot.fixtures import (
    MessageFactory,
    MockMessage,
    _User,
    _UserFactory,
)

CHAT_ID = 'id'
CHAT_TYPE = 'type'
PRIVATE = 'private'


@pytest.fixture
def mock_bot() -> Mock:
    """Mock TeleBot instance."""
    return Mock()


@pytest.fixture
def mock_use_case() -> Mock:
    """Mock use case for handling suggestions."""
    return Mock()


@pytest.fixture
def service(mock_bot: Mock, mock_use_case: Mock) -> SuggestionsHandlerService:
    """Fixture for SuggestionsHandlerService with dependencies injected."""
    return SuggestionsHandlerService(_bot=mock_bot, _use_case=mock_use_case)


class TestSuggestionsHandlerService:
    """Tests for SuggestionsHandlerService."""

    def test_call_with_username_and_text(
        self,
        service: SuggestionsHandlerService,
        mock_use_case: Mock,
        mock_bot: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling a message with a valid username and text."""
        user: _User = tg_message_user_factory.build(username='testuser')
        message: MockMessage = tg_message_factory.build(
            from_user=user,
            text=f'{SUGGEST_COMMAND} Test Title\nTest Description',
            chat={CHAT_ID: 12345, CHAT_TYPE: PRIVATE},
        )

        service(message)  # type: ignore[arg-type]

        mock_use_case.assert_called_once_with(
            tg_username='testuser',
            text=f'{SUGGEST_COMMAND} Test Title\nTest Description',
        )
        mock_bot.send_message.assert_called_once_with(
            chat_id=12345,
            text=SUGGESTION_SAVED,
        )

    def test_call_without_username(
        self,
        service: SuggestionsHandlerService,
        mock_use_case: Mock,
        mock_bot: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling a message when the user has no Telegram username."""
        user: _User = tg_message_user_factory.build(username=None)
        message: MockMessage = tg_message_factory.build(
            from_user=user,
            chat={CHAT_ID: 12345, CHAT_TYPE: PRIVATE},
        )

        service(message)  # type: ignore[arg-type]

        mock_use_case.assert_not_called()
        mock_bot.send_message.assert_called_once_with(
            chat_id=12345,
            text=NO_USERNAME,
        )

    def test_call_without_from_user(
        self,
        service: SuggestionsHandlerService,
        mock_use_case: Mock,
        mock_bot: Mock,
        tg_message_factory: MessageFactory,
    ) -> None:
        """Test handling a message without a `from_user` field."""
        message: MockMessage = tg_message_factory.build(
            from_user=None,
            chat={CHAT_ID: 12345, CHAT_TYPE: PRIVATE},
        )

        service(message)  # type: ignore[arg-type]

        mock_use_case.assert_not_called()
        mock_bot.send_message.assert_called_once_with(
            chat_id=12345,
            text=NO_USER,
        )

    def test_call_without_text(
        self,
        service: SuggestionsHandlerService,
        mock_use_case: Mock,
        mock_bot: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling a message that has no text."""
        user: _User = tg_message_user_factory.build(username='testuser')
        message: MockMessage = tg_message_factory.build(
            from_user=user,
            text=None,
            chat={CHAT_ID: 12345, CHAT_TYPE: PRIVATE},
        )

        service(message)  # type: ignore[arg-type]

        mock_use_case.assert_not_called()
        mock_bot.send_message.assert_called_once_with(
            chat_id=12345,
            text=NO_TEXT,
        )
