from unittest.mock import Mock

from server.apps.tgbot.handlers.start import StartHandlerService


def test_start_handler_service(mock_bot: Mock, message_with_user: Mock) -> None:
    """Test StartHandlerService."""
    StartHandlerService(mock_bot)(message_with_user)

    mock_bot.send_message.assert_called_once_with(
        chat_id=message_with_user.chat.id, text='Hello!'
    )
