from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.surveys.models import Question

QUESTION_TEXT = 'text'


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


@pytest.mark.django_db
def test_delete_question(
    consent_given_question: Question,
    auth_client: APIClient,
) -> None:
    """Test deleting an question by primary key."""
    url = reverse('questions-detail', kwargs={'pk': consent_given_question.pk})
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_not_found_question(auth_client: APIClient) -> None:
    """Test that deleting a nonexistent question returns 404."""
    url = reverse('questions-detail', kwargs={'pk': 1})
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
