from typing import final

from server.apps.surveys.models.surveys import Suggestion
from server.apps.users.models import CustomUser


@final
class SuggestionRepo:
    """Repository for handling Suggestion model operations."""

    def create(
        self, user: CustomUser, title: str, description: str
    ) -> Suggestion:
        """Create a new suggestion in the database.

        Args:
            user: User instance who creates the suggestion
            title: Suggestion title (max 255 characters)
            description: Suggestion description text
        Returns:
            Created Suggestion instance
        """
        return Suggestion.objects.create(
            user=user,
            title=title,
            description=description,
        )
