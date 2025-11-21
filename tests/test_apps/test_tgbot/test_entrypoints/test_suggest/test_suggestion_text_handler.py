from unittest.mock import Mock, patch

from telebot.types import Message

from server.apps.tgbot.entrypoints.suggestions_text import (
    suggestion_text_handler,
)
from server.apps.tgbot.usecases.suggestions import HandleSuggestionTextUseCase


def test_suggestion_text_handler_calls_use_case() -> None:
    """Test that the entrypoint function correctly resolves."""
    mock_message = Mock(spec=Message)
    mock_use_case_instance = Mock()

    with patch(
        'server.apps.tgbot.entrypoints.suggestions_text.resolve'
    ) as mock_resolve:
        mock_resolve.return_value = mock_use_case_instance

        suggestion_text_handler(mock_message)

        mock_resolve.assert_called_once_with(HandleSuggestionTextUseCase)
        mock_use_case_instance.assert_called_once_with(mock_message)
