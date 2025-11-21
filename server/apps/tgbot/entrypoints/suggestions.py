from telebot import TeleBot
from telebot.types import Message

from server.apps.tgbot.constants import SUGGEST_COMMAND
from server.apps.tgbot.usecases.suggestions import HandleSuggestCommandUseCase
from server.di import resolve

bot = resolve(TeleBot)


@bot.message_handler(commands=[SUGGEST_COMMAND.lstrip('/')])  # type: ignore[misc]
def suggest_handler(message: Message) -> None:
    """Entry point for /suggest command."""
    resolve(HandleSuggestCommandUseCase)(message)
