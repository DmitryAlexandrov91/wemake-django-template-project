import pytest
from django.conf import settings

from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.di import resolve


@pytest.mark.django_db
def test_get_stat_settings_db() -> None:
    """Test getting statistics settings from db."""
    repo = resolve(UserStatisticsRepo)
    res = repo.get_stat_settings()
    assert res.pk == 1
    assert res.survey_response_avg_period == settings.DEFAULT_USER_STAT_PERIOD
