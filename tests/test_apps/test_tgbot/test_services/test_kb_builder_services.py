from telebot import types

from server.apps.tgbot.callbacks import answer_callback
from server.apps.tgbot.services.keyboard_builder import (
    ButtonBuilderService,
    KeyboardBuilderService,
)
from server.di import resolve


def test_keyboar_builder_service() -> None:
    """Test that keyboard builder service work correctly."""
    keyboard = resolve(KeyboardBuilderService)()
    assert isinstance(keyboard, types.InlineKeyboardMarkup)


def test_button_builder_service() -> None:
    """Test that button builder service work correctly."""
    keyboard = resolve(KeyboardBuilderService)()
    assert keyboard.keyboard == []

    button = resolve(ButtonBuilderService)(
        text='First_Button',
        callback=answer_callback,
        callback_data={'answer_id': 1, 'survey_result_id': 1},
    )
    keyboard.add(button)
    assert keyboard.keyboard != []
    added_button = keyboard.keyboard[0][0]
    assert isinstance(added_button, types.InlineKeyboardButton)
    assert added_button.text == 'First_Button'
    assert added_button.callback_data == 'edit:1:1'
