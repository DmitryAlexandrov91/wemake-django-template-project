from dataclasses import dataclass

from celery.result import AsyncResult

from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
    UserStatisticsRepo,
)
from server.apps.users.infra.repository import UserRepo, UserRepoSave


@dataclass(frozen=True)
class UpdateSingleUserStatistic:
    """Update user statistics service."""

    _user_repo: UserRepo
    _user_answer_repo: UserAnswerRepo
    _user_statistic_repo: UserStatisticsRepo

    def __call__(  # noqa: WPS602
        self, user_id: int, limit: int
    ) -> None:
        """Updates statistics for one user."""
        user = self._user_repo.get_by_pk(pk=user_id)
        total_time, questions = (
            self._user_answer_repo.get_user_survey_results_aggr(
                user=user, limit=limit
            )
        )
        seconds_per_question = (
            int(total_time.total_seconds() // questions)
            if questions and total_time
            else 0
        )
        self._user_statistic_repo.save_statistics(
            user=user, avg_answer_sec=seconds_per_question
        )


@dataclass(frozen=True)
class GetUserIds:
    """Users list ids service."""

    _user_repo_save: UserRepoSave

    def __call__(self, user_id: int | None = None) -> list[int]:  # noqa: WPS602
        """Gets list of user identifiers."""
        return (
            [user_id]
            if user_id
            else list(self._user_repo_save.get_active_user_ids())
        )


@dataclass(frozen=True)
class GetStatisticPeriod:
    """Statistic settings service."""

    _user_statistic_repo: UserStatisticsRepo

    def __call__(self) -> int:
        """Gets statistics settings."""
        return self._user_statistic_repo.get_stat_settings().survey_response_avg_period  # noqa: E501


@dataclass(frozen=True)
class UpdateStatisticScheduler:
    """Service for call user statistics updates."""

    def __call__(self, user_id: int | None) -> AsyncResult:
        """Starts updating user statistics."""
        from server.apps.surveys.tasks import (  # noqa: PLC0415
            update_user_statistics_task,
        )

        return update_user_statistics_task.delay(user_id=user_id)
