import pytest

from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import Survey
from server.di import resolve


@pytest.mark.django_db
def test_update_survey_partial_data(survey: Survey) -> None:
    """Test SurveyRepo update_survey method with partial data."""
    repo = resolve(SurveyRepo)
    original_description = survey.description

    updated_survey = repo.update_survey(
        survey=survey,
        title='Updated Title',
        description=None,
        department={'name': 'update name'},
    )

    assert updated_survey.pk == survey.pk
    assert updated_survey.title == 'Updated Title'
    assert updated_survey.description == original_description
