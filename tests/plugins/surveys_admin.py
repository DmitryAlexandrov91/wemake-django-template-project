from typing import TypedDict

import pytest
from django.contrib import admin
from django.test import RequestFactory

from server.apps.surveys.admin import StatisticSettingsAdmin
from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.apps.surveys.models import StatisticSettings
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.users import UserBatchFactory


class AdminSetup(TypedDict):
    """Type setting."""

    factory: RequestFactory
    user: CustomUser
    settings_obj: StatisticSettings
    admin: StatisticSettingsAdmin
    users: list[CustomUser]


@pytest.fixture
def save_stat_settings_setup(
    admin_user: CustomUser, user_batch: UserBatchFactory
) -> AdminSetup:
    """Prepare settings for custom admin test."""
    return AdminSetup(
        factory=RequestFactory(),
        user=admin_user,
        settings_obj=resolve(UserStatisticsRepo).get_stat_settings(),
        admin=StatisticSettingsAdmin(StatisticSettings, admin.site),
        users=user_batch(3),
    )
