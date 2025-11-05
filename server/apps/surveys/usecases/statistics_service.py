from dataclasses import dataclass

from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
    UserStatisticsRepo,
)
from server.apps.users.infra.repository import UserRepo, UserRepoSave


@dataclass
class UserStatisticsService:
    """Processing user statistics."""
    _user_repo: UserRepo
    _user_repo_save: UserRepoSave
    _user_answer_repo: UserAnswerRepo
    _user_statistic_repo: UserStatisticsRepo

    def update_single_user_statistics(  # noqa: WPS602
        self, user_id: int, limit: int
    ) -> None:
        """Updates statistics fot one user."""
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

    def get_user_ids(self, user_id: int | None = None) -> list[int]:  # noqa: WPS602
        """Gets list of user identifacators."""
        return (
            [user_id]
            if user_id
            else list(self._user_repo_save.get_active_user_ids())
        )

    def get_statistics_period(self) -> int:  # noqa: WPS602
        """Gets statistics settings."""
        return self._user_statistic_repo.get_stat_settings().survey_response_avg_period

