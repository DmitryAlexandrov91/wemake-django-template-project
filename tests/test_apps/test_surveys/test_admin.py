from collections.abc import Callable
from typing import Any

import pytest
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest

from server.apps.surveys.admin import QuestionAdmin
from server.apps.surveys.models import Question, Survey


@pytest.fixture
def question_admin() -> QuestionAdmin:
    """QuestionAdmin fixture."""
    return QuestionAdmin(Question, AdminSite())


@pytest.mark.django_db
def test_get_surveys(  # noqa: WPS234
    question_admin: QuestionAdmin,
    question_with_two_surveys: Callable[
        [dict[str, Any]], tuple[Question, list[Survey]]
    ],
) -> None:
    """Test get_surveys."""
    question, surveys = question_with_two_surveys({
        'text': 'test text',
        'question_type': 'score',
    })
    result_data: str = question_admin.get_surveys(question)
    expected: str = ', '.join(survey.title for survey in surveys)
    assert result_data == expected


@pytest.mark.django_db
def test_get_surveys_empty(
    question_admin: QuestionAdmin,
    surveys_question_factory: Callable[..., Question],
) -> None:
    """Test empty."""
    question: Question = surveys_question_factory(text='Empty question?')
    assert not question_admin.get_surveys(question)


@pytest.mark.django_db
def test_get_queryset_prefetch(  # noqa: WPS234
    admin_user: Any,
    rf: Any,
    question_with_two_surveys: Callable[
        [dict[str, Any]], tuple[Question, list[Survey]]
    ],
    question_admin: QuestionAdmin,
) -> None:
    """Test prefetch."""
    question, _ = question_with_two_surveys({})
    request: HttpRequest = rf.get('/admin/app/question/')
    request.user = admin_user
    queryset = question_admin.get_queryset(request)
    assert hasattr(queryset, 'prefetch_related')
    assert question in list(queryset)
