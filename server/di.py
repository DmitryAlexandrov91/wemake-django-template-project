import punq
from telebot import TeleBot

from server.apps.company.infra.repository import DepartmentRepo
from server.apps.surveys.infra.repository import QuestionRepo
from server.settings.components import tgbot as settings


def _inject_tg(container: punq.Container) -> None:
    """Register container."""
    container.register(
        TeleBot, instance=TeleBot(settings.BOT_TOKEN), scope='singleton'
    )


def _inject_department_repo(container: punq.Container) -> None:
    """Register DepartmentRepo."""
    container.register(DepartmentRepo)


def _inject_infra(container: punq.Container) -> None:
    """Register repositories."""
    container.register(QuestionRepo)


def create_container() -> punq.Container:
    """Create container."""
    container = punq.Container()
    _inject_tg(container)
    _inject_department_repo(container)
    _inject_infra(container)
    return container


def resolve[Thing](thing: type[Thing]) -> Thing:
    """Resolve thing dependencies."""
    return container.resolve(thing)  # type: ignore[no-any-return]


container = create_container()
