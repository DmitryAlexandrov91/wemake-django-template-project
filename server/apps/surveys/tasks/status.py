from collections.abc import Callable

from celery import group, shared_task

from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.infra.repository import SurveyRepo, SurveySaveRepo
from server.di import resolve

TaskFunction = Callable[[str, str], bool]


@shared_task  # type: ignore[misc]
def turn_one_survey_status_task(survey_id: int) -> None:
    """Celety task for switching one survey status."""
    survey = resolve(SurveySaveRepo).get_by_pk(pk=survey_id)
    resolve(SurveyRepo).update_survey(
        survey=survey, status=SurveyStatus.COMPLETED
    )


@shared_task  # type: ignore[misc]
def turn_survey_active_to_complet_task() -> None:
    """Celery task searches for expired surveys and changes their status."""
    survey_ids = resolve(SurveySaveRepo).get_all_expired_ids()
    update_group = group(
        turn_one_survey_status_task.s(survey_id=survey_id)
        for survey_id in survey_ids
    )
    update_group.apply_async()
