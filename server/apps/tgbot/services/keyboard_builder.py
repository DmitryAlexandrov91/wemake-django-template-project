from dataclasses import dataclass
from typing import Any

from telebot import types


@dataclass(frozen=True, slots=True)
class KeyboardBuilderService:
    """Service for building inline keyboards for Telegram."""

    def __call__(
        self,
        answers: list[Any],
        question_id: int,
        row_width: int = 2,
    ) -> types.InlineKeyboardMarkup:
        """Create inline-keyboard with answers."""
        keyboard = types.InlineKeyboardMarkup(row_width=row_width)  # type: ignore[no-untyped-call]
        buttons = [
            types.InlineKeyboardButton(
                text=answer,
                callback_data=f'answer:{question_id}:{idx}',
            )
            for idx, answer in enumerate(answers, start=1)
        ]
        keyboard.add(*buttons)
        return keyboard
