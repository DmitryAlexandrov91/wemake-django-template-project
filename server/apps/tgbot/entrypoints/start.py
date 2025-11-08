from telebot.types import Message

from server.apps.tgbot.bot_instance import bot
from server.apps.tgbot.handlers.start import StartHandlerService
from server.di import resolve


@bot.message_handler(commands=['start'])  # type: ignore[misc]
def start_handler(message: Message) -> None:
    """Entrypoint for command `/start`."""
    resolve(StartHandlerService)(message)
