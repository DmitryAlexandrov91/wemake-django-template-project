import punq
from telebot import TeleBot

from server.apps.tgbot.keyboards.edit_keyboard import (
    CancelEditAnswerKeyboard,
    EditAnswerKeyboard,
)
from server.apps.tgbot.keyboards.survey_keyboard import SurveyHandleKeyboard
from server.apps.tgbot.services.keyboard_builder import (
    ButtonBuilderService,
    KeyboardBuilderService,
)
from server.apps.tgbot.services.services import TelegramService
from server.apps.tgbot.usecases import (
    ProcessTelegramUpdate,
)
from server.di.tg.handlers import (
    _inject_common_usecases,
    _inject_edit_usecases,
    _inject_entrypoints,
    _inject_start_usecases,
    _inject_survey_usecases,
)
from server.settings.components import tgbot as tg_settings


def _inject_tg(container: punq.Container) -> None:
    """Register TG."""
    container.register(
        TeleBot, instance=TeleBot(tg_settings.BOT_TOKEN), scope='singleton'
    )
    container.register(TelegramService)
    container.register(ProcessTelegramUpdate)


def _inject_handlers(container: punq.Container) -> None:
    """Register handlers."""
    _inject_survey_usecases(container)
    _inject_common_usecases(container)
    _inject_edit_usecases(container)
    _inject_entrypoints(container)
    _inject_start_usecases(container)


def _inject_keyboards(container: punq.Container) -> None:
    """Register keyboards."""
    container.register(KeyboardBuilderService)
    container.register(ButtonBuilderService)
    container.register(EditAnswerKeyboard)
    container.register(CancelEditAnswerKeyboard)
    container.register(SurveyHandleKeyboard)
