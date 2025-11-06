from dataclasses import dataclass

from django.core.exceptions import ValidationError
from telebot import TeleBot, types

from server.apps.surveys.infra.repository import (
    SurveyRepo,
    SurveyResultRepo,
)
from server.apps.users.infra.repository import UserRepo


@dataclass
class HandleStartCommandUseCase:
    """Usecase for survey_res_creation."""

    _user_repo: UserRepo
    _survey_repo: SurveyRepo
    _survey_res_repo: SurveyResultRepo
    _bot: TeleBot

    def execute(self, message: types.Message) -> None:
        """Create survey result."""
        tg_user = message.from_user
        if not tg_user or not tg_user.username:
            raise ValidationError('TG user(name) is not recognized.')
        user = self._user_repo.get_by_tg_username(
            tg_username=f'@{tg_user.username}'
        )
        current_survey = self._survey_repo.get_active_survey_for_user(user=user)
        self._survey_res_repo.get_or_create_user_survey_res(
            user=user,
            survey=current_survey,
        )
