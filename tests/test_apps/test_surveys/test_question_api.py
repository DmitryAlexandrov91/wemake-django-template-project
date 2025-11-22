# flake8: noqa: WPS226
from http import HTTPStatus

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from server.apps.surveys.models import Question, Survey

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
def test_mark_question_to_delete(
    consent_given_question: Question,
    auth_client: APIClient,
) -> None:
    """Test deleting an question by primary key."""
    url = reverse('questions-detail', kwargs={'pk': consent_given_question.pk})
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_200_OK
    consent_given_question.refresh_from_db()
    assert consent_given_question.to_delete is True


@pytest.mark.django_db
def test_mark_to_delete_nonexistent_question(auth_client: APIClient) -> None:
    """Test that deleting a nonexistent question gives error."""
    url = reverse('questions-detail', kwargs={'pk': 1})
    with pytest.raises(ObjectDoesNotExist):
        auth_client.delete(url)


@pytest.mark.django_db
def test_mark_survey_to_delete(
    survey: Survey,
    auth_client: APIClient,
) -> None:
    """Test mark survey to delete by primary key."""
    url = reverse('surveys-detail', kwargs={'pk': survey.pk})
    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_200_OK
    survey.refresh_from_db()
    assert survey.to_delete is True


@pytest.mark.django_db
def test_mark_to_delete_nonexistent_survey(auth_client: APIClient) -> None:
    """Test that deleting a nonexistent question gives error."""
    url = reverse('surveys-detail', kwargs={'pk': 1})
    with pytest.raises(ObjectDoesNotExist):
        auth_client.delete(url)


@pytest.mark.django_db
def test_patch_empty_body_returns_400(
    consent_given_question: Question, auth_client: APIClient
) -> None:
    """PATCH without body must return 400."""
    url = reverse('questions-detail', kwargs={'pk': consent_given_question.pk})
    response = auth_client.patch(url, data={}, format='json')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'PATCH request body cannot be empty.'
