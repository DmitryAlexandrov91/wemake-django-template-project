from typing import Any

import pytest
from django.contrib import admin
from django.http import HttpRequest

from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.apps.surveys.models import Survey
from server.apps.users.admin import CustomUserAdmin
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.surveys_survey import SurveyResultFactory


@pytest.mark.django_db
def test_average_answer_sec_representation(active_user: CustomUser) -> None:
    """Test user statistics representation in user admin."""
    user = active_user
    user_statistics = resolve(UserStatisticsRepo).get_statistics(user=user)
    site = admin.AdminSite()
    adm = CustomUserAdmin(CustomUser, site)
    assert adm.average_answer_sec(user) == user_statistics.average_answer_sec


@pytest.mark.django_db
def test_average_answer_sec_virgin_user(active_user: CustomUser) -> None:
    """Test user statistics representation in virgin user admin."""
    user = active_user
    site = admin.AdminSite()
    adm = CustomUserAdmin(CustomUser, site)
    assert adm.average_answer_sec(user) == 0


@pytest.mark.django_db
def test_useradmin_get_queryset_prefetch(  # noqa: WPS234
    admin_user: Any,
    rf: Any,
    user_admin: CustomUserAdmin,
    survey: Survey,
    surveys_survey_result_factory: SurveyResultFactory,
) -> None:
    """Test prefetch."""
    surveys_survey_result_factory(user=admin_user, survey=survey)
    request: HttpRequest = rf.get('/admin/users/customuser/')
    request.user = admin_user
    queryset = user_admin.get_queryset(request)
    assert hasattr(queryset, 'prefetch_related')
    assert hasattr(queryset, '_prefetch_related_lookups')
