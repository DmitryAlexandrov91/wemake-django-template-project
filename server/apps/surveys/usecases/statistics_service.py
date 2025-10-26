from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
    UserStatisticsRepo,
)
from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.di import resolve


class UserStatisticsService:
    """Processing user statistics."""

    @staticmethod
    def update_single_user_statistics(  # noqa: WPS602
        user_id: int, limit: int
    ) -> None:
        """Updates statistics fot one user."""
        user = resolve(UserRepo).get_by_pk(pk=user_id)
        total_time, questions = resolve(
            UserAnswerRepo
        ).get_user_survey_results_aggr(user=user, limit=limit)
        seconds_per_question = (
            int(total_time.total_seconds() // questions)
            if questions and total_time
            else 0
        )
        resolve(UserStatisticsRepo).save_statistics(
            user=user, avg_answer_sec=seconds_per_question
        )

    @staticmethod
    def get_user_ids(user_id: int | None = None) -> list[int]:  # noqa: WPS602
        """Gets list of user identifacators."""
        return (
            [user_id]
            if user_id
            else list(resolve(UserRepoSave).get_active_user_ids())
        )

    @staticmethod
    def get_statistics_period() -> int:  # noqa: WPS602
        """Gets statistics settings."""
        return (
            resolve(UserStatisticsRepo)
            .get_stat_settings()
            .survey_response_avg_period
        )
