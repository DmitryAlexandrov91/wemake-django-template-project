from unittest.mock import MagicMock

from server.apps.tgbot.entrypoints.menu import menu_handler
from tests.plugins.tgbot.fixtures import MockMessage

CHAT_ID_FIELD = 'chat_id'
TEXT_FIELD = 'text'


def test_menu_handler_sends_main_menu(
    message_with_user: MockMessage,
    mock_bot_send_message: MagicMock,
) -> None:
    """Test the menu_handler entrypoint."""
    menu_handler(message_with_user)

    mock_bot_send_message.assert_called_once()
    args = mock_bot_send_message.call_args.kwargs
    assert args[CHAT_ID_FIELD] == message_with_user.chat.id
    assert args[TEXT_FIELD] == 'Выберите действие:'
    buttons = [
        btn.callback_data
        for row in args['reply_markup'].keyboard
        for btn in row
    ]
    assert set(buttons) == {
        'show_all_archive_answers',
        'show_archive_answers_for_period',
    }
