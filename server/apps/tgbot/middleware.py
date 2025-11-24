from typing import Any, override

from telebot import TeleBot, types
from telebot.handler_backends import BaseMiddleware
from telebot.states.sync.context import StateContext
from telebot.util import update_types


class StateMiddleware(BaseMiddleware):
    """Middleware for state."""

    def __init__(self, bot: TeleBot) -> None:
        """StateMiddleware init."""
        self.update_sensitive = False
        self.update_types = update_types
        self.bot: TeleBot = bot

    @override
    def pre_process(self, message: types.Message, data: dict[str, Any]) -> None:  # noqa: WPS110
        """Pre process method."""
        state_context = StateContext(message, self.bot)  # type: ignore[arg-type]
        data['state'] = state_context

    @override
    def post_process(
        self,
        message: types.Message,
        data: dict[str, Any],  # noqa: WPS110
        exception: Exception,
    ) -> None:
        """Post process method."""
