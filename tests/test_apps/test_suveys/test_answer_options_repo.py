import pytest

from server.apps.surveys.infra.repository import AnswerOptionRepo
from server.apps.surveys.models import AnswerOption, Question

pytestmark = pytest.mark.django_db


@pytest.fixture
def repo() -> AnswerOptionRepo:
    """Fixture to create a repository."""
    return AnswerOptionRepo()


@pytest.fixture
def question() -> Question:
    """Fixture to create a question."""
    return Question.objects.create(text='Test question', question_type='score')


@pytest.fixture
def options(question: Question) -> list[AnswerOption]:
    """Fixture to create answer options."""
    return [
        AnswerOption.objects.create(question=question, text='test1'),
        AnswerOption.objects.create(question=question, text='test2'),
    ]


def test_get_all_answer_options(
    repo: AnswerOptionRepo, options: list[AnswerOption]
) -> None:
    """get_all returns all answer options."""
    options_list = repo.get_all()

    assert len(options_list) == 2
    assert options_list[0].text == 'test1'
    assert options_list[1].text == 'test2'


def test_get_all_returns_empty_list(repo: AnswerOptionRepo) -> None:
    """get_all returns empty list if there are no options."""
    AnswerOption.objects.all().delete()
    assert repo.get_all() == []


def test_get_by_pk(repo: AnswerOptionRepo, options: list[AnswerOption]) -> None:
    """get_by_pk returns the answer option with the given pk."""
    option = options[0]
    option_by_pk = repo.get_by_pk(option.pk)
    assert option_by_pk is not None
    assert option_by_pk.pk == option.pk
    assert option_by_pk.text == 'test1'


def test_get_by_pk_returns_none(repo: AnswerOptionRepo) -> None:
    """get_by_pk returns none when given a wrong pk."""
    assert repo.get_by_pk(99999) is None
