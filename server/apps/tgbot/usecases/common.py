from dataclasses import dataclass

from telebot import TeleBot

from server.apps.surveys.infra.repository import (
    QuestionRepo,
    SurveyResultRepo,
    UserAnswerRepo,
)
from server.apps.surveys.models.surveys import (
    AnswerOption,
    Question,
    SurveyResult,
)
from server.apps.surveys.usecases.advance_to_next_question import (
    AdvanceToNextQuestion,
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


@dataclass
class ProcessingAnswerUseCase:
    """Usecase for proceccing answer to question."""

    _bot: TeleBot
    _survey_result_repo: SurveyResultRepo
    _question_repo: QuestionRepo
    _save_answer_use_case: SaveAnswerUseCase
    _advance_to_next_question: AdvanceToNextQuestion

    def __call__(
        self,
        survey_result_id: int,
        question_id: int,
        answer_option: str,
    ) -> SurveyResult:
        """Proceccing answer for question, returns SurveyResult."""
        survey_result = self._survey_result_repo.get_by_pk(pk=survey_result_id)
        question = self._question_repo.get_by_pk(pk=question_id)
        self._save_answer_use_case(
            survey_result=survey_result,
            question=question,
            answer_text=answer_option,
        )
        return self._advance_to_next_question(survey_result=survey_result)
