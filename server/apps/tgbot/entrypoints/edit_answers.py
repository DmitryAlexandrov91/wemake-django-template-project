import telebot
from telebot.types import Message

from server.apps.tgbot.bot_instance import bot
from server.apps.tgbot.callbacks import answer_callback, answer_cancel_callback
from server.apps.tgbot.handlers.edit import EditHandlerService
from server.apps.tgbot.states import EditStates
from server.di import resolve


@bot.message_handler(commands=['edit'])  # type: ignore[misc]
def responses_edit_handler(message: Message) -> None:
    """Entrypoint for command `/edit`."""
    resolve(EditHandlerService)(message)


@bot.callback_query_handler(
    func=answer_callback.filter.check  # type: ignore[misc, no-untyped-call]
)
def handle_edit_answer(
    call: telebot.types.CallbackQuery,
) -> None:
    """Handle edit answer."""
    resolve(EditHandlerService).enter_new_text(call=call)


@bot.callback_query_handler(  # type: ignore[misc, no-untyped-call]
    func=answer_cancel_callback.filter.check
)
def handle_cancel_edit_answer(
    call: telebot.types.CallbackQuery,
) -> None:
    """Handle edit cancel button."""
    resolve(EditHandlerService).cancel(call=call)


@bot.message_handler(
    state=EditStates.waiting_for_new_answer,
    content_types=['text'],  # type: ignore[misc]
)
def handle_new_answer_text(message: Message) -> None:
    """Handle new answer text input when in waiting state."""
    resolve(EditHandlerService).process_new_answer_text(message)
