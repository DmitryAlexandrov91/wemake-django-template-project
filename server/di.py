import punq
from django.conf import LazySettings, settings
from telebot import TeleBot

from server.apps.company.infra.repository import DepartmentRepo
from server.apps.surveys.infra.repository import (
    AnswerOptionRepo,
    QuestionRepo,
    SurveyRepo,
)
from server.apps.tgbot.handlers.start import StartHandlerService
from server.apps.tgbot.logic.usecases import ProcessTelegramUpdate
from server.apps.tgbot.services import TelegramService
from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.apps.users.services import AuthService
from server.settings.components import tgbot as tg_settings


def _inject_settings(container: punq.Container) -> None:
    """Register settings."""
    container.register(LazySettings, instance=settings, scope='singleton')


def _inject_tg(container: punq.Container) -> None:
    """Register TG."""
    container.register(
        TeleBot, instance=TeleBot(tg_settings.BOT_TOKEN), scope='singleton'
    )
    container.register(TelegramService)
    container.register(ProcessTelegramUpdate)
    container.register(StartHandlerService)


def _inject_department_repo(container: punq.Container) -> None:
    """Register DepartmentRepo."""
    container.register(DepartmentRepo)


def _inject_infra(container: punq.Container) -> None:
    """Register repositories."""
    container.register(QuestionRepo)
    container.register(AnswerOptionRepo)
    container.register(UserRepo)
    container.register(UserRepoSave)
    container.register(SurveyRepo)


def _inject_auth_service(container: punq.Container) -> None:
    """Register AuthService."""
    container.register(AuthService)


def create_container() -> punq.Container:
    """Create container."""
    container = punq.Container()
    _inject_tg(container)
    _inject_department_repo(container)
    _inject_infra(container)
    _inject_auth_service(container)
    _inject_settings(container)
    return container


def resolve[Thing](thing: type[Thing]) -> Thing:
    """Resolve thing dependencies."""
    return container.resolve(thing)  # type: ignore[no-any-return]


container = create_container()
