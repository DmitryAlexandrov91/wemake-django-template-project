from collections.abc import Callable

import pytest

from server.apps.surveys.infra.repository import AnswerOptionRepo
from server.apps.surveys.models import AnswerOption, Question
from server.di import resolve
from tests.plugins.surveys import AnswerOptionFactory


@pytest.mark.django_db
def test_repo_get_by_pk(
    surveys_answer_option_factory: AnswerOptionFactory,
    consent_given_question: Question,
) -> None:
    """Test AnswerOptionRepo get_by_pk method."""
    repo = resolve(AnswerOptionRepo)

    with pytest.raises(AnswerOption.DoesNotExist):
        repo.get_by_pk(pk=2)

    test_answer_option = surveys_answer_option_factory()
    created_option = repo.get_by_pk(pk=test_answer_option.pk)

    assert isinstance(created_option, AnswerOption)
    assert created_option.text == test_answer_option.text


@pytest.mark.django_db
def test_repo_get_all(
    surveys_answer_option_batch: Callable[[int], list[AnswerOption]],
) -> None:
    """Test AnswerOptionRepo get_all method."""
    repo = resolve(AnswerOptionRepo)
    batch_size = 3
    created_options = surveys_answer_option_batch(batch_size)
    options = repo.get_all()

    assert options.count() == batch_size
    assert all(isinstance(option, AnswerOption) for option in options)
    assert set(options) == set(created_options)
