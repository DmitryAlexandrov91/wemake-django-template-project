from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from server.apps.tgbot.constants import SUGGEST_COMMAND
from server.apps.tgbot.entrypoints.suggestions import suggest_handler


@pytest.fixture
def mock_message() -> Mock:
    """Fixture that provides a mock Telegram message."""
    message = Mock()
    message.text = f'{SUGGEST_COMMAND} Test Title'
    return message


@pytest.fixture
def mock_suggestions_service() -> Mock:
    """Fixture that provides a mock SuggestionsHandlerService."""
    return Mock()


@pytest.fixture
def mock_resolve(mock_suggestions_service: Mock) -> Generator[Mock, None, None]:
    """Fixture that patches resolve to return our mock service."""
    with patch(
        'server.apps.tgbot.entrypoints.suggestions.resolve'
    ) as mock_resolve_fn:
        mock_resolve_fn.return_value = mock_suggestions_service
        yield mock_resolve_fn


def test_suggest_handler_calls_service(
    mock_resolve: Mock,
    mock_suggestions_service: Mock,
    mock_message: Mock,
) -> None:
    """Test that suggest_handler resolves and calls the service."""
    suggest_handler(mock_message)

    mock_resolve.assert_called_once()
    mock_suggestions_service.assert_called_once_with(mock_message)
