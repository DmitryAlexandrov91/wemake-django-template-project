from dataclasses import dataclass
from typing import Any

from telebot import types

from server.apps.tgbot.callbacks import CallbackFactory


@dataclass(frozen=True, slots=True)
class KeyboardBuilderService:
    """Service for building inline keyboards for Telegram."""

    def __call__(
        self,
        row_width: int = 1,
    ) -> types.InlineKeyboardMarkup:
        """Create InlineKeyboardMarkup obj."""
        return types.InlineKeyboardMarkup(row_width=row_width)  # type: ignore[no-untyped-call]


@dataclass(frozen=True, slots=True)
class ButtonBuilderService:
    """Service to adding buttons for inline keyboard."""

    def __call__(
        self,
        text: str,
        callback: CallbackFactory,
        callback_data: dict[str, Any],
    ) -> types.InlineKeyboardButton:
        """Create InlineKeyboardButton obj."""
        return types.InlineKeyboardButton(
            text=text,
            callback_data=callback.factory.new(**callback_data),
        )
