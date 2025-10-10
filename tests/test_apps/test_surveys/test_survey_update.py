import pytest

from server.apps.company.models import Department
from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import Survey
from server.apps.surveys.serializers_create import SurveyUpdateSerializer
from server.di import resolve


@pytest.mark.django_db
def test_survey_update_serializer_integration(
    survey: Survey, department: Department
) -> None:
    """Integration test for SurveyUpdateSerializer with actual repo."""
    validated_data = {
        'title': 'Updated Title',
        'department_name': department.name,
    }

    serializer = SurveyUpdateSerializer()
    upd_survey = serializer.update(survey, validated_data)

    assert upd_survey.pk == survey.pk
    assert upd_survey.title == 'Updated Title'


@pytest.mark.django_db
def test_update_survey_partial_data(survey: Survey) -> None:
    """Test SurveyRepo update_survey method with partial data."""
    repo = resolve(SurveyRepo)
    original_description = survey.description

    updated_survey = repo.update_survey(
        survey=survey,
        title='New Title',
        description=None,
    )

    assert updated_survey.pk == survey.pk
    assert updated_survey.title == 'New Title'
    assert updated_survey.description == original_description


@pytest.mark.django_db
def test_update_survey_without_department_name(survey: Survey) -> None:
    """Test updating survey without changing department."""
    repo = resolve(SurveyRepo)
    original_department = survey.department

    updated_survey = repo.update_survey(
        survey=survey,
        title='New_Title',
        description='Updated description',
    )

    assert updated_survey.title == 'New_Title'
    assert updated_survey.description == 'Updated description'
    assert updated_survey.department == original_department
