import pytest
from django.contrib.auth import get_user_model

from server.apps.surveys.infra.suggestion_repository import SuggestionRepo
from server.apps.surveys.models.surveys import Suggestion

User = get_user_model()


@pytest.mark.django_db
def test_create_suggestion() -> None:
    """Test creating a suggestion successfully."""
    repo = SuggestionRepo()
    user = User.objects.create(
        email='test@example.com',
        full_name='Test User',
    )
    title = 'Test Suggestion Title'
    description = 'Test suggestion description'

    suggestion = repo.create(user, title, description)

    assert suggestion.user == user
    assert suggestion.title == title
    assert suggestion.description == description
    assert Suggestion.objects.filter(id=suggestion.id).exists()


@pytest.mark.django_db
def test_create_suggestion_max_title_length() -> None:
    """Test creating suggestion with maximum title length."""
    repo = SuggestionRepo()
    user = User.objects.create(
        email='test2@example.com',
        full_name='Test User 2',
    )
    long_title = 'A' * 255
    description = 'Test description'

    suggestion = repo.create(user, long_title, description)

    assert suggestion.title == long_title
    assert len(suggestion.title) == 255
