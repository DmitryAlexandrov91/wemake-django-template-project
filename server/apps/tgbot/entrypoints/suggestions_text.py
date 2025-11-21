from telebot import TeleBot
from telebot.types import Message

from server.apps.tgbot.states import SuggestState
from server.apps.tgbot.usecases.suggestions import HandleSuggestionTextUseCase
from server.di import resolve

bot = resolve(TeleBot)


@bot.message_handler(state=SuggestState.waiting_for_suggestion)  # type: ignore[misc]
def suggestion_text_handler(message: Message) -> None:
    """Entry point for suggestion text after /suggest."""
    resolve(HandleSuggestionTextUseCase)(message)
