import pytest

from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import Survey
from server.di import resolve
from tests.plugins.surveys_survey import SurveyResultFactory, UserAnswerFactory


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


@pytest.mark.django_db
def test_get_result_method(
    survey: Survey,
    surveys_survey_result_factory: SurveyResultFactory,
    surveys_user_answer_result_factory: UserAnswerFactory,
) -> None:
    """Test get_result_method of SurveyRepo."""
    repo = resolve(SurveyRepo)
    new_survey_result = surveys_survey_result_factory(survey=survey)
    surveys_user_answer_result_factory(survey_result=new_survey_result)
    survey_results = repo.get_results(survey.pk)
    assert len(survey_results) == 1
    assert survey_results[0].survey == survey
