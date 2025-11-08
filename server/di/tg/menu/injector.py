import punq

from server.di.tg.menu.services import _inject_menu_services
from server.di.tg.menu.use_case import _inject_menu_use_cases


def _inject_menu(container: punq.Container) -> None:
    _inject_menu_use_cases(container)
    _inject_menu_services(container)
