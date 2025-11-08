import telebot
from telebot.types import Message

from server.apps.tgbot.handlers.start import StartHandlerService
from server.di import resolve

bot = resolve(telebot.TeleBot)


@bot.message_handler(commands=['start'])  # type: ignore[misc]
def start_handler(message: Message) -> None:
    """Entrypoint for command `/start`."""
    resolve(StartHandlerService)(message)
