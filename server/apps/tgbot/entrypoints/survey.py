import telebot
from telebot.types import Message

from server.apps.tgbot.callbacks import (
    survey_callback,
)
from server.apps.tgbot.handlers.survey import SurveyHandlerService
from server.apps.tgbot.states import SurveyResponseState
from server.di import resolve

bot = resolve(telebot.TeleBot)


@bot.message_handler(commands=['survey'])  # type: ignore[misc]
def survey_handler(message: Message) -> None:
    """Handle completing the survey."""
    resolve(SurveyHandlerService)(message=message)


@bot.message_handler(  # type: ignore[misc]
    state=SurveyResponseState.survey_response,
)
def handle_survey_text_answer_response(message: Message) -> None:
    """Handle user text response for survey answer."""
    resolve(SurveyHandlerService).handle_text_answer(message=message)


@bot.callback_query_handler(  # type: ignore[misc, no-untyped-call]
    func=survey_callback.filter.check
)
def handle_survey_callback_answer_response(
    call: telebot.types.CallbackQuery,
) -> None:
    """Handle button response for survey answer."""
    resolve(SurveyHandlerService).handle_callback_answer(call=call)
