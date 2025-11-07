from collections.abc import Callable

from celery import group, shared_task
from django.core.mail import send_mail

from server.apps.surveys.infra.repository import QuestionRepo, SurveySaveRepo
from server.apps.surveys.usecases.statistics_service import (
    UserStatisticsService,
)
from server.di import resolve

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


@shared_task  # type: ignore[misc]
def delete_one_survey_task(survey_id: int) -> None:
    """Celery task for deletion of one department."""
    resolve(SurveySaveRepo).delete(pk=survey_id)


@shared_task  # type: ignore[misc]
def delete_one_question_task(question_id: int) -> None:
    """Celery task for deletion of one department."""
    resolve(QuestionRepo).delete(pk=question_id)


@shared_task  # type: ignore[misc]
def delete_marked_surveys_task() -> None:
    """Celery task for deletion of all marked surveys."""
    survey_ids = resolve(SurveySaveRepo).get_all_to_delete_ids()
    update_group = group(
        delete_one_survey_task.s(survey_id=survey_id)
        for survey_id in survey_ids
    )
    update_group.apply_async()


@shared_task  # type: ignore[misc]
def delete_marked_questions_task() -> None:
    """Celery task for deletion of all marked questions."""
    questions_ids = resolve(QuestionRepo).get_all_to_delete_ids()
    update_group = group(
        delete_one_question_task.s(question_id=question_id)
        for question_id in questions_ids
    )
    update_group.apply_async()


@shared_task  # type: ignore[misc]
def email_survey_invitation_task(
    subject: str,
    message: str,
    from_email: str,
    to_emails: list[str],
) -> None:
    """Celery task to send survey inviatation email."""
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=to_emails,
        fail_silently=True,
    )
