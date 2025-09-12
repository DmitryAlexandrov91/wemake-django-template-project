from http import HTTPStatus

import pytest
from django.db.models import QuerySet
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.surveys.models import Question
from server.apps.surveys.views import QuestionViewSet

QUESTION_TEXT = 'text'


@pytest.mark.django_db
def test_get_queryset_returns_queryset() -> None:
    """Test that get_queryset returns a QuerySet."""
    viewset = QuestionViewSet()
    queryset = viewset.get_queryset()

    assert isinstance(queryset, QuerySet)
    assert queryset.model is Question


@pytest.mark.django_db
def test_patch_success(
    consent_given_question: Question, auth_client: APIClient
) -> None:
    """Successfully partial updating a question."""
    url = reverse('questions-detail', kwargs={'pk': consent_given_question.pk})
    payload = {QUESTION_TEXT: 'Test text', 'question_type': 'score'}
    response = auth_client.patch(url, payload, format='json')
    response_data = response.json()

    assert response.status_code == HTTPStatus.ACCEPTED
    assert response_data[QUESTION_TEXT] != consent_given_question.text
    assert response_data[QUESTION_TEXT] == payload[QUESTION_TEXT]
    assert response_data['question_type'] == payload['question_type']
    assert response_data['is_favorite'] is False
