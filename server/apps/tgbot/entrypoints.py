import telebot
from telebot.types import Message

from server.apps.tgbot.callbacks import (
    answer_callback,
    answer_cancel_callback,
    survey_callback,
)
from server.apps.tgbot.handlers.edit import EditHandlerService
from server.apps.tgbot.handlers.start import StartHandlerService
from server.apps.tgbot.handlers.survey import SurveyHandlerService
from server.apps.tgbot.states import EditState, SurveyResponseState
from server.di import resolve

bot = resolve(telebot.TeleBot)


@bot.message_handler(commands=['start'])  # type: ignore[misc]
def start_handler(message: Message) -> None:
    """Entrypoint for command `/start`."""
    resolve(StartHandlerService)(message)


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
    state=EditState.waiting_for_new_answer,
    content_types=['text'],  # type: ignore[misc]
)
def handle_new_answer_text(message: Message) -> None:
    """Handle new answer text input when in waiting state."""
    resolve(EditHandlerService).process_new_answer_text(message)


@bot.message_handler(commands=['survey'])  # type: ignore[misc]
def survey_handler(message: Message) -> None:
    """Handle completing the survey."""
    resolve(SurveyHandlerService)(message=message)


@bot.message_handler(
    state=SurveyResponseState.survey_response,
    content_types=['text'],  # type: ignore[misc]
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
