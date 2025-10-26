import punq
from telebot import TeleBot

from server.apps.tgbot.handlers.edit import EditHandlerService
from server.apps.tgbot.handlers.start import StartHandlerService
from server.apps.tgbot.keyboards.edit_keyboard import (
    CancelEditAnswerKeyboard,
    EditAnswerKeyboard,
)
from server.apps.tgbot.logic.edit_handler_usecases import (
    HandleCancelEditResponseUseCase,
    HandleEditCommandUseCase,
    HandleEditResponseUseCase,
    HandleProcessEditResponseUseCase,
)
from server.apps.tgbot.logic.usecases import (
    HandleStartCommandUseCase,
    ProcessTelegramUpdate,
)
from server.apps.tgbot.services.keyboard_builder import (
    ButtonBuilderService,
    KeyboardBuilderService,
)
from server.apps.tgbot.services.services import TelegramService
from server.settings.components import tgbot as tg_settings


def _inject_tg(container: punq.Container) -> None:
    """Register TG."""
    container.register(
        TeleBot, instance=TeleBot(tg_settings.BOT_TOKEN), scope='singleton'
    )
    container.register(TelegramService)
    container.register(ProcessTelegramUpdate)


def _inject_handlers(container: punq.Container) -> None:
    container.register(StartHandlerService)
    container.register(HandleStartCommandUseCase)
    container.register(EditHandlerService)
    container.register(HandleEditCommandUseCase)
    container.register(HandleEditResponseUseCase)
    container.register(HandleCancelEditResponseUseCase)
    container.register(HandleProcessEditResponseUseCase)


def _inject_keyboards(container: punq.Container) -> None:
    container.register(KeyboardBuilderService)
    container.register(ButtonBuilderService)
    container.register(EditAnswerKeyboard)
    container.register(CancelEditAnswerKeyboard)
