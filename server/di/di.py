import punq
from django.conf import LazySettings, settings

from server.apps.company.infra.repository import DepartmentRepo
from server.apps.surveys.infra.repository import (
    AnswerOptionRepo,
    QuestionRepo,
    SurveyRepo,
    SurveyResultRepo,
    SurveySaveRepo,
    UserAnswerRepo,
    UserStatisticsRepo,
)
from server.apps.surveys.infra.suggestion_repository import SuggestionRepo
from server.apps.surveys.usecases.advance_to_next_question import (
    AdvanceToNextQuestion,
)
from server.apps.surveys.usecases.statistics_services import (
    GetStatisticPeriod,
    GetUserIds,
    UpdateSingleUserStatistic,
    UpdateStatisticScheduler,
)
from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.apps.users.services import AuthService
from server.di.tg import (
    _inject_handlers,
    _inject_keyboards,
    _inject_menu,
    _inject_tg,
)


def _inject_settings(container: punq.Container) -> None:
    """Register settings."""
    container.register(LazySettings, instance=settings, scope='singleton')


def _inject_infra(container: punq.Container) -> None:
    """Register repositories."""
    container.register(UserRepo)
    container.register(UserRepoSave)
    container.register(DepartmentRepo)
    container.register(UserAnswerRepo)
    container.register(UserStatisticsRepo)
    container.register(SuggestionRepo)


def _inject_survey_infra(container: punq.Container) -> None:
    """Register survey and relation repositories."""
    container.register(SurveyRepo)
    container.register(SurveyResultRepo)
    container.register(SurveySaveRepo)
    container.register(UserStatisticsRepo)
    container.register(QuestionRepo)
    container.register(AnswerOptionRepo)


def _inject_services(container: punq.Container) -> None:
    """Register services."""
    container.register(UpdateStatisticScheduler)
    container.register(AuthService)
    container.register(AdvanceToNextQuestion)
    container.register(UpdateSingleUserStatistic)
    container.register(GetUserIds)
    container.register(GetStatisticPeriod)


def create_container() -> punq.Container:
    """Create container."""
    container = punq.Container()
    _inject_tg(container)
    _inject_infra(container)
    _inject_services(container)
    _inject_settings(container)
    _inject_survey_infra(container)
    _inject_handlers(container)
    _inject_keyboards(container)
    _inject_menu(container)
    return container


def resolve[Thing](thing: type[Thing]) -> Thing:
    """Resolve thing dependencies."""
    return container.resolve(thing)  # type: ignore[no-any-return]


container = create_container()
