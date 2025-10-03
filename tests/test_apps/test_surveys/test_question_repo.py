import pytest

from server.apps.surveys.choices import QuestionType
from server.apps.surveys.infra.repository import QuestionRepo
from server.apps.surveys.models import Question, Survey
from server.di import resolve
from tests.plugins.surveys import QuestionFactory


@pytest.mark.django_db
def test_repo_get_by_pk(consent_given_question: Question) -> None:
    """Test QuestionRepo get_by_pk method."""
    repo = resolve(QuestionRepo)
    with pytest.raises(Question.DoesNotExist):
        repo.get_by_pk(pk=consent_given_question.pk + 1)

    created_question = repo.get_by_pk(pk=consent_given_question.pk)

    assert isinstance(created_question, Question)
    assert created_question.text == consent_given_question.text


@pytest.mark.django_db
def test_repo_get_all(surveys_question_factory: QuestionFactory) -> None:
    """Test QuestionRepo get_all method."""
    repo = resolve(QuestionRepo)
    batch_size = 2

    for batch_number in range(batch_size):
        surveys_question_factory(
            text=f'Question {batch_number}',
            question_type=QuestionType.CONSENT_GIVEN,
        )

    questions = repo.get_all()

    assert questions.count() == batch_size
    assert all(isinstance(question, Question) for question in questions)


@pytest.mark.django_db
def test_update_question(consent_given_question: Question) -> None:
    """Test QuestionRepo update_question method changes question text."""
    repo = resolve(QuestionRepo)
    original_text = consent_given_question.text
    upd_question_obj = repo.update_question(
        question=consent_given_question, text='New text'
    )
    assert upd_question_obj.text == 'New text'
    assert upd_question_obj.text != original_text


@pytest.mark.django_db
def test_update_question_surveys(
    consent_given_question: Question, two_surveys: list[Survey]
) -> None:
    """Test QuestionRepo update_question sets surveys for question."""
    repo = QuestionRepo()
    assert consent_given_question.surveys.count() == 0
    repo.update_question(question=consent_given_question, surveys=two_surveys)
    updated_surveys = list(consent_given_question.surveys.all())
    assert all(survey in updated_surveys for survey in two_surveys)
    assert consent_given_question.surveys.count() == len(two_surveys)
