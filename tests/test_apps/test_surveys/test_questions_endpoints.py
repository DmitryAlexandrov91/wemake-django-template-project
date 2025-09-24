from collections.abc import Callable

import pytest
from django.test import Client
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK as OK

from server.apps.surveys.models import Question
from server.apps.users.models import CustomUser
from tests.plugins import users_auth
from tests.test_apps.test_users.services import get_user_json

DATA_ATTR = 'data'
ID_ATTR = 'id'
TEXT_ATTR = 'text'
QUESTION_TYPE_ATTR = 'question_type'
IS_FAVORITE_ATTR = 'is_favorite'
FILTER_ATTR = 'filter'
ORDER_ATTR = 'order'
ASC_PARAM = 'asc'
DESC_PARAM = 'des'
PAGINATION_FIELDS = (
    'page',
    'per_page',
    'total',
    'num_pages',
    'has_next',
    'has_previous',
)


@pytest.fixture
def questions_url() -> str:
    """Return questions endpoint URL."""
    return reverse('questions-list')


@pytest.fixture
def authenticated_client(
    client: Client,
    user: CustomUser,
    password: str,
) -> Client:
    """Return authenticated client."""
    client.post(users_auth.LOGIN_URL, data=get_user_json(user.email, password))
    return client


@pytest.mark.django_db
def test_get_all_questions_response(
    client: Client,
    user: CustomUser,
    password: str,
    questions_url: str,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Test success response status of questions endpoint."""
    client.post(users_auth.LOGIN_URL, data=get_user_json(user.email, password))
    questions_batch(2)

    response = client.get(questions_url)
    response_data = response.json()

    assert response.status_code == OK
    assert len(response_data[DATA_ATTR]) == 2


@pytest.mark.django_db(transaction=True)
def test_filter_favorite_questions(
    authenticated_client: Client,
    questions_url: str,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Test filtering favorite questions."""
    Question.objects.all().delete()
    all_questions = questions_batch(2)
    all_questions[0].is_favorite = True
    all_questions[0].save()
    all_questions[1].is_favorite = False
    all_questions[1].save()

    response = authenticated_client.get(
        f'{questions_url}?{FILTER_ATTR}=favorite'
    )
    response_data = response.json()
    questions_data = response_data[DATA_ATTR]

    assert response.status_code == OK
    assert len(questions_data) == 1
    assert questions_data[0][ID_ATTR] == all_questions[0].id
    assert questions_data[0][IS_FAVORITE_ATTR] is True


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    ('order_param', 'expected_index'),
    [
        (ASC_PARAM, 0),
        (DESC_PARAM, 1),
    ],
)
def test_order_questions(
    authenticated_client: Client,
    questions_url: str,
    questions_batch: Callable[[int], list[Question]],
    order_param: str,
    expected_index: int,
) -> None:
    """Test ordering questions in both directions."""
    questions = questions_batch(2)

    response = authenticated_client.get(
        f'{questions_url}?{ORDER_ATTR}={order_param}'
    )
    response_data = response.json()
    questions_data = response_data[DATA_ATTR]

    assert response.status_code == OK
    assert len(questions_data) == 2
    assert questions_data[0][TEXT_ATTR] == questions[expected_index].text


@pytest.mark.django_db
def test_question_response_structure(
    authenticated_client: Client,
    questions_url: str,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Test that question response has correct structure."""
    questions_batch(1, is_favorite=True)  # type: ignore[call-arg]

    response = authenticated_client.get(questions_url)
    response_data = response.json()
    questions_data = response_data[DATA_ATTR]

    assert response.status_code == OK
    assert len(questions_data) >= 1

    question_response = questions_data[0]
    expected_fields = {ID_ATTR, TEXT_ATTR, QUESTION_TYPE_ATTR, IS_FAVORITE_ATTR}
    assert all(field in question_response for field in expected_fields)
    assert question_response[IS_FAVORITE_ATTR] is True


@pytest.mark.django_db
def test_pagination_for_questions(
    authenticated_client: Client,
    questions_url: str,
    questions_batch: Callable[[int], list[Question]],
) -> None:
    """Test pagination works for questions endpoint."""
    questions_batch(5)

    response = authenticated_client.get(f'{questions_url}?per_page=2&page=1')
    response_data = response.json()

    assert response.status_code == OK
    assert len(response_data[DATA_ATTR]) == 2

    assert all(field in response_data for field in PAGINATION_FIELDS)
