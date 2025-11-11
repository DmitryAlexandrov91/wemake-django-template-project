from dataclasses import dataclass

from server.apps.surveys.infra.suggestion_repository import SuggestionRepo
from server.apps.tgbot.constants import SUGGEST_COMMAND
from server.apps.users.infra.repository import UserRepo


@dataclass
class HandleSuggestionUseCase:
    """Use case for processing and saving user suggestions."""

    suggestion_repo: SuggestionRepo
    user_repo: UserRepo

    def __call__(self, tg_username: str, text: str) -> None:
        """Process suggestion text and save it to the database."""
        title, description = self._extract_title_and_description(text)

        user = self.user_repo.get_by_tg_username(f'@{tg_username}')

        self.suggestion_repo.create(
            user=user,
            title=title,
            description=description,
        )

    def _extract_title_and_description(self, text: str) -> tuple[str, str]:
        """
        Extract title and description from the user's suggestion message.

        The expected format of the message:
            `SUGGEST_COMMAND` <title>
            <optional description>

        Returns:
            A tuple (title, description) trimmed to safe limits.
        """
        clean_text = text.replace(SUGGEST_COMMAND, '').strip()
        lines = clean_text.split('\n', 1)

        title = lines[0].strip()[:255]  # noqa: WPS432
        description = lines[1].strip() if len(lines) > 1 else ''

        return title, description
