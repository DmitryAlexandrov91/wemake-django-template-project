import punq

from server.apps.tgbot.logic.menu.services import PeriodBase


def _inject_menu_services(container: punq.Container) -> None:
    container.register(PeriodBase)
