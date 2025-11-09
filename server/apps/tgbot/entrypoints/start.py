import telebot
from telebot.types import Message

from server.apps.tgbot.usecases.start import HandleStartCommandUseCase
from server.di import resolve

bot = resolve(telebot.TeleBot)


@bot.message_handler(commands=['start'])  # type: ignore[misc]
def start_handler(message: Message) -> None:
    """Entrypoint for command `/start`."""
    resolve(HandleStartCommandUseCase)(message)
    bot.send_message(chat_id=message.chat.id, text='Hello!')
