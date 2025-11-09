import punq

from server.apps.tgbot.usecases import (
    HandleStartCommandUseCase,
    SaveAnswerUseCase,
)
from server.apps.tgbot.usecases.common import ProcessingAnswerUseCase
from server.apps.tgbot.usecases.edit import (
    HandleCancelEditResponseUseCase,
    HandleEditCommandUseCase,
    HandleEditResponseUseCase,
    HandleProcessEditResponseUseCase,
)
from server.apps.tgbot.usecases.survey import (
    HandleSurveyCallbackResponseUseCase,
    HandleSurveyCommandUseCase,
    HandleSurveyMessageResponseUseCase,
)


def _inject_start_usecases(container: punq.Container) -> None:
    """Register start command usecases."""
    container.register(HandleStartCommandUseCase)


def _inject_edit_usecases(container: punq.Container) -> None:
    """Register edit command usecases."""
    container.register(HandleEditCommandUseCase)
    container.register(HandleEditResponseUseCase)
    container.register(HandleCancelEditResponseUseCase)
    container.register(HandleProcessEditResponseUseCase)


def _inject_survey_usecases(container: punq.Container) -> None:
    """Register survey command usecases."""
    container.register(HandleSurveyCommandUseCase)
    container.register(HandleSurveyMessageResponseUseCase)
    container.register(HandleSurveyCallbackResponseUseCase)


def _inject_common_usecases(container: punq.Container) -> None:
    """Register common tg usecases."""
    container.register(SaveAnswerUseCase)
    container.register(ProcessingAnswerUseCase)
