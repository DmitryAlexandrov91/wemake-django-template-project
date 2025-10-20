from collections.abc import Callable

from celery import group, shared_task

from server.apps.surveys.usecases.statistics_service import (
    UserStatisticsService,
)

TaskFunction = Callable[[str, str], bool]


@shared_task  # type: ignore[misc]
def update_one_user_statistics_task(user_id: int, period: int) -> None:
    """Celery task for updating one user statistics."""
    UserStatisticsService.update_single_user_statistics(
        user_id=user_id, limit=period
    )


@shared_task  # type: ignore[misc]
def update_user_statistics_task(user_id: int | None = None) -> None:
    """Updates employee statistics when admin sets new statistic settings."""
    period = UserStatisticsService.get_statistics_period()
    user_ids = UserStatisticsService.get_user_ids(user_id)
    update_group = group(
        update_one_user_statistics_task.s(user_id=user_id, period=period)
        for user_id in user_ids
    )
    update_group.apply_async()
