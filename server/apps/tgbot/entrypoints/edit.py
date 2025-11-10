from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from server.apps.tgbot.callbacks import (
    answer_callback,
    answer_cancel_callback,
)
from server.apps.tgbot.states import EditState
from server.apps.tgbot.usecases.edit import (
    HandleCancelEditResponseUseCase,
    HandleEditCommandUseCase,
    HandleEditResponseUseCase,
    HandleProcessEditResponseUseCase,
)
from server.di import resolve

bot = resolve(TeleBot)


@bot.message_handler(commands=['edit'])  # type: ignore[misc]
def responses_edit_handler(message: Message) -> None:
    """Entrypoint for command `/edit`."""
    resolve(HandleEditCommandUseCase)(message)


@bot.callback_query_handler(
    func=answer_callback.filter.check  # type: ignore[misc, no-untyped-call]
)
def handle_edit_answer(
    call: CallbackQuery,
) -> None:
    """Handle edit answer."""
    resolve(HandleEditResponseUseCase)(call)


@bot.callback_query_handler(  # type: ignore[misc, no-untyped-call]
    func=answer_cancel_callback.filter.check
)
def handle_cancel_edit_answer(
    call: CallbackQuery,
) -> None:
    """Handle edit cancel button."""
    resolve(HandleCancelEditResponseUseCase)(call)


@bot.message_handler(  # type: ignore[misc]
    state=EditState.waiting_for_new_answer,
)
def handle_new_answer_text(message: Message) -> None:
    """Handle new answer text input when in waiting state."""
    resolve(HandleProcessEditResponseUseCase)(message)
