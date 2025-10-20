from typing import Any

import pytest
from telebot import types

from server.apps.tgbot.services.keyboard_builder import KeyboardBuilderService
from server.di import resolve


@pytest.mark.parametrize(
    ('answers', 'question_id', 'row_width'),
    [
        (['Yes', 'No'], 1, 2),
        (list(range(1, 10)), 5, 3),
    ],
)
def test_build_multiple_choice_keyboard(
    answers: list[Any], question_id: int, row_width: int
) -> None:
    """Test that multiple choice keyboard is built correctly."""
    builder = resolve(KeyboardBuilderService)
    keyboard = builder(
        answers=answers, question_id=question_id, row_width=row_width
    )

    assert isinstance(keyboard, types.InlineKeyboardMarkup)
