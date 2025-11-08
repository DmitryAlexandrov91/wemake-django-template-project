import pytest
from django.db import models

from server.apps.company.models import Department
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
    survey = surveys_survey_factory(department=department)
    survey_result = fakery_m(SurveyResult)(
        user=user, survey=survey, current_question=fakery_m(Question)()
    )
    fakery_m(SurveyQuestion)(survey=survey)
    for _ in range(3):
        fakery_m(UserAnswer)(survey_result=survey_result)

    return message_with_user
