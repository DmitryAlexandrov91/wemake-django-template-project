from collections.abc import Callable
from typing import Final

import pytest

from server.apps.surveys.infra.repository import SurveyResultRepo
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    SurveyResult,
    UserAnswer,
)
from server.apps.surveys.usecases.advance_to_next_question import (
    AdvanceToNextQuestion,
)

_CURRENT_QUESTION_FIELD: Final = 'current_question'


@pytest.mark.django_db
def test_save_answer_creates_user_answer(
    surveys_survey_result_factory: Callable[[], SurveyResult],
    surveys_question_factory: Callable[..., Question],
) -> None:
    """Test saving answer creates a UserAnswer."""
    survey_result = surveys_survey_result_factory()

    question = surveys_question_factory(survey=survey_result.survey)
    survey_result.current_question = question
    survey_result.save(update_fields=[_CURRENT_QUESTION_FIELD])

    repo = SurveyResultRepo()
    answer = repo.save_answer(survey_result, text_answer='Hello')

    assert UserAnswer.objects.count() == 1
    assert answer.text_answer == 'Hello'
    assert answer.survey_result == survey_result


@pytest.mark.django_db
def test_advance_to_next_question(
    surveys_survey_result_factory: Callable[[], SurveyResult],
    surveys_question_factory: Callable[..., Question],
) -> None:
    """Test advancing sets next question or None if last."""
    survey_result = surveys_survey_result_factory()

    questions = [
        surveys_question_factory(survey=survey_result.survey),
        surveys_question_factory(survey=survey_result.survey),
        surveys_question_factory(survey=survey_result.survey),
    ]

    survey_result.current_question = questions[0]
    survey_result.save(update_fields=[_CURRENT_QUESTION_FIELD])

    usecase = AdvanceToNextQuestion()
    updated_result = usecase(survey_result)
    assert updated_result.current_question == questions[1]

    updated_result = usecase(updated_result)
    assert updated_result.current_question == questions[2]

    updated_result = usecase(updated_result)
    assert updated_result.current_question is None


@pytest.mark.django_db
def test_save_answer_raises_if_no_question(
    surveys_survey_result_factory: Callable[[], SurveyResult],
) -> None:
    """save_answer should raise if current_question = None."""
    survey_result = surveys_survey_result_factory()
    survey_result.current_question = None
    survey_result.save(update_fields=[_CURRENT_QUESTION_FIELD])

    repo = SurveyResultRepo()
    with pytest.raises(ValueError, match='Survey has no current question'):
        repo.save_answer(survey_result, text_answer='test')


@pytest.mark.django_db
def test_advance_with_no_current_question(
    surveys_survey_result_factory: Callable[[], SurveyResult],
) -> None:
    """If current_question is None, survey_result remains unchanged."""
    survey_result = surveys_survey_result_factory()
    survey_result.current_question = None
    survey_result.save(update_fields=[_CURRENT_QUESTION_FIELD])

    usecase = AdvanceToNextQuestion()
    updated_result = usecase(survey_result)

    assert updated_result.current_question is None


@pytest.mark.django_db
def test_save_answer_with_selected_options(
    surveys_survey_result_factory: Callable[[], SurveyResult],
    surveys_question_factory: Callable[..., Question],
    surveys_answer_option_factory: Callable[..., AnswerOption],
) -> None:
    """Check that save_answer saves selected_options on UserAnswer."""
    survey_result = surveys_survey_result_factory()
    question = surveys_question_factory(survey=survey_result.survey)

    options = [
        surveys_answer_option_factory(question=question, text='Opt 1'),
        surveys_answer_option_factory(question=question, text='Opt 2'),
    ]

    survey_result.current_question = question
    survey_result.save(update_fields=[_CURRENT_QUESTION_FIELD])

    user_answer = SurveyResultRepo().save_answer(
        survey_result,
        selected_options=options,
    )

    assert {opt.pk for opt in user_answer.selected_options.all()} == {
        opt.pk for opt in options
    }
