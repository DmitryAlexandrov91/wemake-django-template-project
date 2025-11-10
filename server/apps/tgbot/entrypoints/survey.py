from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from server.apps.surveys.models.surveys import SurveyResult
from server.apps.tgbot.callbacks import (
    survey_callback,
)
from server.apps.tgbot.states import SurveyResponseState
from server.apps.tgbot.usecases.survey.callback_handle import (
    HandleSurveyCallbackResponseUseCase,
)
from server.apps.tgbot.usecases.survey.message_handle import (
    HandleSurveyMessageResponseUseCase,
)
from server.apps.tgbot.usecases.survey.survey_begin import (
    HandleSurveyCommandUseCase,
)
from server.di import resolve

bot = resolve(TeleBot)


@bot.message_handler(commands=['survey'])  # type: ignore[misc]
def survey_handler(message: Message, survey_result: SurveyResult) -> None:
    """Handle completing the survey."""
    resolve(HandleSurveyCommandUseCase)(
        message=message, survey_result=survey_result
    )


@bot.message_handler(  # type: ignore[misc]
    state=SurveyResponseState.survey_response,
)
def handle_survey_text_answer_response(message: Message) -> None:
    """Handle user text response for survey answer."""
    resolve(HandleSurveyMessageResponseUseCase)(message)


@bot.callback_query_handler(  # type: ignore[misc, no-untyped-call]
    func=survey_callback.filter.check
)
def handle_survey_callback_answer_response(
    call: CallbackQuery,
) -> None:
    """Handle button response for survey answer."""
    resolve(HandleSurveyCallbackResponseUseCase)(call)
