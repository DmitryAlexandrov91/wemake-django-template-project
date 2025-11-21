from unittest.mock import MagicMock, Mock

import pytest
from telebot import types

from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.message_templates import (
    EMPTY_SUGGESTION,
    NO_USER,
    NO_USERNAME,
    SUGGESTION_REQUEST,
    SUGGESTION_SAVED,
)
from server.apps.tgbot.usecases.suggestions import (
    HandleSuggestCommandUseCase,
    HandleSuggestionTextUseCase,
)
from tests.plugins.tgbot.fixtures import (
    MessageFactory,
    _User,
    _UserFactory,
)

USER_ID = 98765
CHAT_ID = 12345
CHAT_TYPE = 'private'
USERNAME = 'testuser'
SUGGESTION_TEXT = 'This is a test suggestion'


@pytest.fixture
def mock_bot() -> Mock:
    """Mock TeleBot instance."""
    return Mock()


@pytest.fixture
def mock_suggestion_usecase() -> Mock:
    """Mock HandleSuggestionUseCase."""
    return Mock()


@pytest.fixture
def handle_suggest_command_use_case(
    mock_bot: Mock,
) -> HandleSuggestCommandUseCase:
    """Fixture for HandleSuggestCommandUseCase."""
    return HandleSuggestCommandUseCase(
        _bot=mock_bot,
        _state=StatePostgresStorage(),
    )


@pytest.fixture
def handle_suggestion_text_use_case(
    mock_bot: Mock, mock_suggestion_usecase: Mock
) -> HandleSuggestionTextUseCase:
    """Fixture for HandleSuggestionTextUseCase."""
    return HandleSuggestionTextUseCase(
        _bot=mock_bot,
        _suggestion_usecase=mock_suggestion_usecase,
        _state=StatePostgresStorage(),
    )


class TestHandleSuggestCommandUseCase:
    """Tests for HandleSuggestCommandUseCase."""

    @pytest.mark.django_db
    def test_call_with_valid_user(
        self,
        handle_suggest_command_use_case: HandleSuggestCommandUseCase,
        mock_bot: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling /suggest command with valid user."""
        user: _User = tg_message_user_factory.build(username=USERNAME)
        message: types.Message = tg_message_factory.build(  # type: ignore[assignment]
            from_user=user,
            chat={'id': CHAT_ID, 'type': CHAT_TYPE},  # noqa: WPS226
        )

        handle_suggest_command_use_case(message)

        mock_bot.add_custom_filter.assert_called_once()

        mock_bot.send_message.assert_called_once_with(
            chat_id=CHAT_ID, text=SUGGESTION_REQUEST
        )

    def test_call_without_from_user(
        self,
        handle_suggest_command_use_case: HandleSuggestCommandUseCase,
        mock_bot: Mock,
        tg_message_factory: MessageFactory,
        mock_set_state: MagicMock,
    ) -> None:
        """Test handling /suggest command without from_user."""
        message: types.Message = tg_message_factory.build(  # type: ignore[assignment]
            from_user=None,
            chat={'id': CHAT_ID, 'type': CHAT_TYPE},
        )

        handle_suggest_command_use_case(message)

        mock_bot.send_message.assert_called_once_with(CHAT_ID, NO_USER)
        mock_set_state.assert_not_called()


class TestHandleSuggestionTextUseCase:
    """Tests for HandleSuggestionTextUseCase."""

    @pytest.mark.django_db
    def test_call_with_valid_data(
        self,
        handle_suggestion_text_use_case: HandleSuggestionTextUseCase,
        mock_bot: Mock,
        mock_suggestion_usecase: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling suggestion text with valid data."""
        user: _User = tg_message_user_factory.build(
            id=USER_ID, username=USERNAME, first_name='Test', last_name='User'
        )
        message: types.Message = tg_message_factory.build(  # type: ignore[assignment]
            from_user=user,
            text=SUGGESTION_TEXT,
            chat={'id': CHAT_ID, 'type': CHAT_TYPE},
        )

        handle_suggestion_text_use_case(message)

        mock_suggestion_usecase.assert_called_once_with(
            tg_username=USERNAME, text=SUGGESTION_TEXT
        )
        mock_bot.send_message.assert_called_once_with(
            chat_id=CHAT_ID, text=SUGGESTION_SAVED
        )

    def test_call_without_from_user(
        self,
        handle_suggestion_text_use_case: HandleSuggestionTextUseCase,
        mock_bot: Mock,
        mock_suggestion_usecase: Mock,
        tg_message_factory: MessageFactory,
    ) -> None:
        """Test handling suggestion text without from_user."""
        message: types.Message = tg_message_factory.build(  # type: ignore[assignment]
            from_user=None,
            text=SUGGESTION_TEXT,
            chat={'id': CHAT_ID, 'type': CHAT_TYPE},
        )

        handle_suggestion_text_use_case(message)

        mock_suggestion_usecase.assert_not_called()
        mock_bot.send_message.assert_called_once_with(CHAT_ID, NO_USER)
        mock_bot.delete_state.assert_not_called()

    def test_call_without_username(
        self,
        handle_suggestion_text_use_case: HandleSuggestionTextUseCase,
        mock_bot: Mock,
        mock_suggestion_usecase: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling suggestion text without username."""
        user: _User = tg_message_user_factory.build(username=None)
        message: types.Message = tg_message_factory.build(  # type: ignore[assignment]
            from_user=user,
            text=SUGGESTION_TEXT,
            chat={'id': CHAT_ID, 'type': CHAT_TYPE},
        )

        handle_suggestion_text_use_case(message)

        mock_suggestion_usecase.assert_not_called()
        mock_bot.send_message.assert_called_once_with(CHAT_ID, NO_USERNAME)
        mock_bot.delete_state.assert_not_called()

    def test_call_without_text(
        self,
        handle_suggestion_text_use_case: HandleSuggestionTextUseCase,
        mock_bot: Mock,
        mock_suggestion_usecase: Mock,
        tg_message_factory: MessageFactory,
        tg_message_user_factory: _UserFactory,
    ) -> None:
        """Test handling suggestion text without text."""
        user: _User = tg_message_user_factory.build(username=USERNAME)
        message: types.Message = tg_message_factory.build(  # type: ignore[assignment]
            from_user=user,
            text=None,
            chat={'id': CHAT_ID, 'type': CHAT_TYPE},
        )

        handle_suggestion_text_use_case(message)

        mock_suggestion_usecase.assert_not_called()
        mock_bot.send_message.assert_called_once_with(CHAT_ID, EMPTY_SUGGESTION)
        mock_bot.delete_state.assert_not_called()
