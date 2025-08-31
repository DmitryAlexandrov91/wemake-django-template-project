import pytest

from server.apps.surveys.choices import QuestionType
from server.apps.surveys.infra.repository import QuestionRepo
from server.apps.surveys.models import Question
from server.di import resolve
from tests.plugins.surveys import QuestionFactory


@pytest.mark.django_db
def test_repo_get_by_pk(consent_given_question: Question) -> None:
    """Test QuestionRepo get_by_pk method."""
    repo = resolve(QuestionRepo)

    with pytest.raises(Question.DoesNotExist):
        repo.get_by_pk(pk=2)

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
