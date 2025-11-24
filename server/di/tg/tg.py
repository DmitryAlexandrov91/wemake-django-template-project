import punq
from telebot import TeleBot
from telebot.custom_filters import StateFilter

from server.apps.tgbot.buttons.back_to_surveys import BackToSurveysButton
from server.apps.tgbot.infra.storage import StatePostgresStorage
from server.apps.tgbot.keyboards.edit_keyboard import (
    CancelEditAnswerKeyboard,
    EditAnswerKeyboard,
    SurveysListKeyboard,
)
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.middleware import StateMiddleware
from server.apps.tgbot.services.keyboard_builder import (
    ButtonBuilderService,
    KeyboardBuilderService,
)
from server.apps.tgbot.services.telegram_service import TelegramService
from server.di.tg.handlers import (
    _inject_common_usecases,
    _inject_edit_usecases,
    _inject_start_usecases,
    _inject_suggestions_usecases,
    _inject_survey_usecases,
)
from server.settings.components import tgbot as tg_settings


def _inject_tg(container: punq.Container) -> None:
    """Register TG."""
    state_storage = StatePostgresStorage()
    bot = TeleBot(
        token=tg_settings.BOT_TOKEN,
        state_storage=state_storage,
        use_class_middlewares=True,
    )
    bot.add_custom_filter(StateFilter(bot))  # type: ignore[no-untyped-call]
    bot.setup_middleware(StateMiddleware(bot))
    container.register(
        service=TeleBot,
        instance=bot,
        scope='singleton',
    )
    container.register(TelegramService)
    container.register(StatePostgresStorage, instance=state_storage)


def _inject_handlers(container: punq.Container) -> None:
    """Register handlers."""
    _inject_survey_usecases(container)
    _inject_common_usecases(container)
    _inject_edit_usecases(container)
    _inject_start_usecases(container)
    _inject_suggestions_usecases(container)


def _inject_keyboards(container: punq.Container) -> None:
    """Register keyboards."""
    container.register(KeyboardBuilderService)
    container.register(ButtonBuilderService)
    container.register(EditAnswerKeyboard)
    container.register(CancelEditAnswerKeyboard)
    container.register(SurveyHandleKeyboard)
    container.register(SurveysListKeyboard)
    container.register(BackToSurveysButton)
