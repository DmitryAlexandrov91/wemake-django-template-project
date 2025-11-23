from datetime import timedelta

import pytest
from django.db import models
from django.utils import timezone

from server.apps.company.models import Department
from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.models import SurveyQuestion, SurveyResult, UserAnswer
from server.apps.surveys.models.surveys import Question
from tests.plugins.fakery import FakeryM
from tests.plugins.surveys_survey import SurveyFactory
from tests.plugins.tgbot.fixtures import MockMessage
from tests.plugins.users import UserFactory


@pytest.fixture
def user_from_message_with_relations(
    message_with_user: MockMessage,
    user_factory: UserFactory,
    department: Department,
    surveys_survey_factory: SurveyFactory,
    fakery_m: FakeryM[models.Model],
) -> MockMessage:
    """Create CustomUser obj from MockMessage with necessary relations.

    And returns MockMessage
    """
    tg_user = message_with_user.from_user
    assert tg_user is not None
    user = user_factory(
        tg_username=f'@{tg_user.username}', department=department
    )
    survey = surveys_survey_factory(
        start_date=timezone.now().date() - timedelta(days=1),
        end_date=timezone.now().date() + timedelta(days=5),
        status=SurveyStatus.ACTIVE,
        department=department,
    )

    first_question = fakery_m(Question)()
    survey_result = fakery_m(SurveyResult)(
        user=user, survey=survey, current_question=first_question
    )
    fakery_m(SurveyQuestion)(survey=survey, question=first_question)
    for _ in range(3):
        fakery_m(UserAnswer)(survey_result=survey_result)
        fakery_m(SurveyQuestion)(survey=survey, question=fakery_m(Question)())

    return message_with_user
