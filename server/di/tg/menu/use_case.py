import punq

from server.apps.tgbot.logic.menu.all_answer_usecase import (
    ShowAllArchiveAnswers,
)
from server.apps.tgbot.logic.menu.answer_period_usecase import (
    FinalizePeriodAnswers,
    InitiatePeriodAnswers,
    RequestStartDateForPeriod,
)
from server.apps.tgbot.logic.menu.usecases import (
    GetCompletedSurveyrs,
    SendMenuUseCase,
)


def _inject_menu_use_cases(container: punq.Container) -> None:
    container.register(SendMenuUseCase)
    container.register(ShowAllArchiveAnswers)
    container.register(InitiatePeriodAnswers)
    container.register(FinalizePeriodAnswers)
    container.register(RequestStartDateForPeriod)
    container.register(GetCompletedSurveyrs)
