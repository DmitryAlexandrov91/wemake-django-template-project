import pytest
from django.db import models

from server.apps.surveys.infra.repository import UserAnswerRepo
from server.apps.surveys.models import SurveyResult, UserAnswer
from server.di import resolve
from tests.plugins.fakery import FakeryM


@pytest.mark.django_db
def test_get_answers_by_survey_result(fakery_m: FakeryM[models.Model]) -> None:
    """Test get_answers_by_survey_result method of UserAnswer repo."""
    survey_result = fakery_m(SurveyResult)()
    batch = 3
    for _ in range(batch):
        fakery_m(UserAnswer)(survey_result=survey_result)

    survey_result_answers = resolve(
        UserAnswerRepo
    ).get_answers_by_survey_result(survey_result=survey_result)  # type: ignore[arg-type]

    assert survey_result_answers.count() == batch
    for answer in survey_result_answers:
        assert answer.survey_result == survey_result


@pytest.mark.django_db
def test_edit_text(fakery_m: FakeryM[UserAnswer]) -> None:
    """Test user answer repo edit text method."""
    answer_text = 'BeforeChange'
    new_answer_text = 'AfterChange'
    user_answer = fakery_m(UserAnswer)(text_answer=answer_text)

    assert user_answer.text_answer == answer_text

    updated_user_answer = resolve(UserAnswerRepo).edit_text(
        answer_id=user_answer.pk,
        new_text_answer=new_answer_text,
    )

    assert isinstance(user_answer, UserAnswer)
    assert updated_user_answer.text_answer == new_answer_text
