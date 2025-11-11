from unittest.mock import Mock

from server.apps.tgbot.constants import SUGGEST_COMMAND
from server.apps.tgbot.logic.suggestions_usecases import HandleSuggestionUseCase


class TestHandleSuggestionUseCase:
    """Tests for HandleSuggestionUseCase."""

    def test_call_with_both_fields(self) -> None:
        """Should create suggestion with title and description."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)

        use_case('testuser', 'Test Title\nTest Description')  # noqa: WPS226

        user_repo.get_by_tg_username.assert_called_once_with('@testuser')
        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='Test Title',
            description='Test Description',  # noqa: WPS226
        )

    def test_call_with_title_only(self) -> None:
        """Should create suggestion with title only (no description)."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)

        use_case('testuser', 'Test Title Only')

        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='Test Title Only',
            description='',
        )

    def test_call_truncates_long_title(self) -> None:
        """Should truncate title to 255 characters if it's too long."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)
        long_text = f'{"A" * 300}\nTest Description'  # noqa: WPS237

        use_case('testuser', long_text)

        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='A' * 255,
            description='Test Description',
        )

    def test_call_with_command_prefix(self) -> None:
        """Should remove 'SUGGEST_COMMAND' command from text."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)

        use_case('testuser', f'{SUGGEST_COMMAND} Test Title\nTest Description')

        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='Test Title',
            description='Test Description',
        )

    def test_call_with_whitespace(self) -> None:
        """Should trim whitespace from title and description."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)

        use_case('testuser', '  Test Title  \n  Test Description  ')

        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='Test Title',
            description='Test Description',
        )

    def test_call_with_only_command(self) -> None:
        """Should handle case when only command is provided."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)

        use_case('testuser', SUGGEST_COMMAND)

        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='',
            description='',
        )

    def test_call_with_command_and_whitespace(self) -> None:
        """Should handle command with trailing whitespace."""
        repo = Mock()
        user_repo = Mock()
        user_repo.get_by_tg_username.return_value = Mock()

        use_case = HandleSuggestionUseCase(repo, user_repo)

        use_case('testuser', f'{SUGGEST_COMMAND}   ')

        repo.create.assert_called_once_with(
            user=user_repo.get_by_tg_username.return_value,
            title='',
            description='',
        )
