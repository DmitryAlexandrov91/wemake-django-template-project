import pytest

from server.apps.surveys.infra.repository import AnswerOptionRepo
from server.apps.surveys.models import AnswerOption, Question
from server.di import resolve
from tests.plugins.surveys import AnswerOptionFactory


@pytest.mark.django_db
def test_repo_get_by_pk(test_answer_option: AnswerOption) -> None:
    """Test AnswerOptionRepo get_by_pk method."""
    repo = resolve(AnswerOptionRepo)

    non_existent_option = repo.get_by_pk(pk=999999)
    assert non_existent_option is None

    found_option = repo.get_by_pk(pk=test_answer_option.pk)

    assert found_option is not None
    assert isinstance(found_option, AnswerOption)
    assert found_option.text == test_answer_option.text
    assert found_option.question == test_answer_option.question


@pytest.mark.django_db
def test_repo_get_all(
    surveys_answer_option_factory: AnswerOptionFactory,
    consent_given_question: Question,
) -> None:
    """Test AnswerOptionRepo get_all method."""
    repo = resolve(AnswerOptionRepo)
    batch_size = 3

    for num in range(batch_size):
        surveys_answer_option_factory(
            question=consent_given_question,
            text=f'Option {num}',
        )

    options = repo.get_all()

    assert len(options) == batch_size
    assert all(isinstance(option, AnswerOption) for option in options)

    question_ids = {option.question_id for option in options}
    assert len(question_ids) == 1
    assert next(iter(question_ids)) == consent_given_question.pk
