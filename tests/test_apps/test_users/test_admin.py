import pytest
from django.contrib import admin

from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.apps.users.admin import CustomUserAdmin
from server.apps.users.models import CustomUser
from server.di import resolve


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
