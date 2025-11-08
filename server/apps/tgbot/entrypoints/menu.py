import telebot
from telebot.types import Message

from server.apps.tgbot.bot_instance import bot
from server.apps.tgbot.logic.menu.all_answer_usecase import (
    ShowAllArchiveAnswers,
)
from server.apps.tgbot.logic.menu.answer_period_usecase import (
    FinalizePeriodAnswers,
    InitiatePeriodAnswers,
    RequestStartDateForPeriod,
)
from server.apps.tgbot.logic.menu.usecases import SendMenuUseCase
from server.apps.tgbot.states import SurveyPeriodStates
from server.di import resolve


@bot.message_handler(commands=['menu'])  # type: ignore[misc]
def menu_handler(message: Message) -> None:
    """Entrypoint for command `/menu`."""
    resolve(SendMenuUseCase)(message)


@bot.callback_query_handler(
    func=lambda call: call.data == 'show_all_archive_answers'
)  # type: ignore[misc, no-untyped-call]
def handle_show_archive_answers(call: telebot.types.CallbackQuery) -> None:
    """Handle 'view_answers' callback to show user's answers."""
    resolve(ShowAllArchiveAnswers)(call)


@bot.callback_query_handler(
    func=lambda call: call.data == 'show_archive_answers_for_period'
)  # type: ignore[misc, no-untyped-call]
def handle_archive_answers_for_period(
    call: telebot.types.CallbackQuery,
) -> None:
    """Handle callback to view archive answers for a selected period."""
    resolve(InitiatePeriodAnswers)(call)


@bot.message_handler(
    state=SurveyPeriodStates.waiting_for_start_date,
    content_types=['text'],  # type: ignore[misc]
)
def handle_start_date(message: telebot.types.Message) -> None:
    """Receive and process the start date from user input."""
    resolve(RequestStartDateForPeriod)(message)


@bot.message_handler(
    state=SurveyPeriodStates.waiting_for_end_date,
    content_types=['text'],  # type: ignore[misc]
)
def handle_end_date(message: telebot.types.Message) -> None:
    """Receive and process the end date from user input."""
    resolve(FinalizePeriodAnswers)(message)
