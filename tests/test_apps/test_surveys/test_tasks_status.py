import pytest
from celery.result import EagerResult

from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.infra.repository import SurveySaveRepo
from server.apps.surveys.models import Survey
from server.apps.surveys.tasks.status import (
    turn_one_survey_status_task,
    turn_survey_active_to_complet_task,
)
from server.di import resolve


@pytest.mark.django_db
def test_switch_one_survey_status_task(survey: Survey) -> None:
    """Test survey switching from active to completed status celery task."""
    survey_id = survey.id
    assert survey.status != SurveyStatus.COMPLETED
    task_result: EagerResult = turn_one_survey_status_task.delay(survey_id)
    task_result.get(timeout=5)
    assert task_result.state == 'SUCCESS'
    updated_survey = resolve(SurveySaveRepo).get_by_pk(pk=survey_id)
    assert updated_survey.status == SurveyStatus.COMPLETED


@pytest.mark.django_db
def test_switch_two_surveys_status_task(
    two_expired_surveys: list[Survey],
) -> None:
    """Test bulk surveys remarking celery task."""
    survey_ids = [survey.id for survey in two_expired_surveys]
    turn_survey_active_to_complet_task.delay()
    for survey_id in survey_ids:
        updated_survey = resolve(SurveySaveRepo).get_by_pk(pk=survey_id)
        assert updated_survey.status == SurveyStatus.COMPLETED
