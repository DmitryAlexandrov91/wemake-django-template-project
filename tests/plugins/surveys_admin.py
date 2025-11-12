from typing import TypedDict

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from server.apps.surveys.admin import (
    QuestionAdmin,
    StatisticSettingsAdmin,
    UserAnswerAdmin,
)
from server.apps.surveys.infra.repository import UserStatisticsRepo
from server.apps.surveys.models import (
    Question,
    StatisticSettings,
    UserAnswer,
)
from server.apps.users.models import CustomUser
from server.di import resolve
from tests.plugins.users import UserBatchFactory


@pytest.fixture
def question_admin_instance() -> QuestionAdmin:
    """QuestionAdmin instance fixture."""
    return QuestionAdmin(Question, AdminSite())


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


@pytest.fixture
def user_answer_admin_instance() -> UserAnswerAdmin:
    """UserAnswerAdmin instance fixture."""
    return UserAnswerAdmin(model=UserAnswer, admin_site=AdminSite())
