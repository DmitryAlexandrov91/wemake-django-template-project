import punq
from telebot import TeleBot

from server.apps.surveys.infra.repository import AnswerOptionRepo
from server.settings.components import tgbot as settings


def _inject_tg(container: punq.Container) -> None:
    """Register container."""
    container.register(
        TeleBot, instance=TeleBot(settings.BOT_TOKEN), scope='singleton'
    )


def _inject_repositories(container: punq.Container) -> None:
    """Register repositories."""
    container.register(AnswerOptionRepo, scope='singleton')


def create_container() -> punq.Container:
    """Create container."""
    container = punq.Container()
    _inject_tg(container)
    _inject_repositories(container)
    return container


def resolve[Thing](thing: type[Thing]) -> Thing:
    """Resolve thing dependencies."""
    return container.resolve(thing)  # type: ignore[no-any-return]


container = create_container()
