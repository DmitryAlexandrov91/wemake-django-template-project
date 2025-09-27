from unittest.mock import Mock, patch

from server.apps.tgbot.handlers.start import StartHandlerService
from server.apps.tgbot.logic.usecases import HandleStartCommandUseCase


@patch('server.apps.users.infra.repository.UserRepo')
@patch('server.apps.surveys.infra.repository.SurveyRepo')
@patch('server.apps.surveys.infra.repository.SurveyResultRepo')
def test_start_handler_service_new(
    mock_survey_res_repo: Mock,
    mock_survey_repo: Mock,
    mock_user_repo: Mock,
    mock_bot: Mock,
    message_with_user: Mock,
) -> None:
    """Test StartHandlerService."""
    mock_user = Mock()
    mock_survey = Mock()
    mock_user_repo.get_by_tg_username.return_value = mock_user
    mock_survey_repo.get_active_survey_for_user.return_value = mock_survey
    mock_survey_res_repo.get_or_create_user_survey_res.return_value = None
    handle_start_use_case = HandleStartCommandUseCase(
        _user_repo=mock_user_repo,
        _survey_repo=mock_survey_repo,
        _survey_res_repo=mock_survey_res_repo,
        _bot=mock_bot,
    )
    service = StartHandlerService(
        bot=mock_bot, handle_start_use_case=handle_start_use_case
    )
    service(message_with_user)
    mock_survey_repo.get_active_survey_for_user.assert_called_once_with(
        user=mock_user
    )
    mock_survey_res_repo.get_or_create_user_survey_res.assert_called_once_with(
        user=mock_user, survey=mock_survey
    )
    mock_bot.send_message.assert_called_once_with(
        chat_id=message_with_user.chat.id, text='Hello!'
    )
