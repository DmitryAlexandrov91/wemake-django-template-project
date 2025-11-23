import pytest
from django.db import models

from server.apps.surveys.infra.survey_question_repo import SurveyQuestionRepo
from server.apps.surveys.models.surveys import Question, Survey, SurveyQuestion
from server.di import resolve
from tests.plugins.fakery import FakeryM


@pytest.mark.django_db
def test_get_survey_question_next_question(
    fakery_m: FakeryM[models.Model],
) -> None:
    """Test ensure that get_survey_question_next_question method.

    works correctly.
    """
    survey = fakery_m(Survey)(title='Survey Question Repo Test')
    current_question = fakery_m(Question)(text='First question')
    next_question = fakery_m(Question)(text='Next question')
    for question in current_question, next_question:
        fakery_m(SurveyQuestion)(survey=survey, question=question)

    survey_question_next_question = resolve(
        SurveyQuestionRepo
    ).get_survey_question_next_question(
        survey=survey,  # type:ignore[arg-type]
        current_question=current_question,  # type:ignore[arg-type]
    )

    assert survey_question_next_question is not None
    assert survey_question_next_question.pk == next_question.pk
