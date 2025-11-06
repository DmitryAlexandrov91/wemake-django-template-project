from dataclasses import dataclass

from telebot import TeleBot

from server.apps.surveys.infra.repository import (
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import (
    AnswerOption,
    Question,
    SurveyResult,
)
from server.apps.tgbot.services.services import TelegramService


@dataclass
class ProcessTelegramUpdate:
    """Usecase for process update bot."""

    _telegram_service: TelegramService

    def __call__(self, request_body: bytes) -> None:
        """Use service for bot update."""
        self._telegram_service.process_update(request_body)


@dataclass
class SaveAnswerUseCase:
    """Usecase for user answers save."""

    _bot: TeleBot
    _user_answer_repo: UserAnswerRepo

    def __call__(
        self,
        answer_text: str,
        survey_result: SurveyResult,
        question: Question,
        selected_options: list[AnswerOption] | None = None,
    ) -> None:
        """Create answer object from message."""
        self._user_answer_repo.save_user_answer(
            survey_result=survey_result,
            question=question,
            text_answer=answer_text,
            selected_options=selected_options,
        )
