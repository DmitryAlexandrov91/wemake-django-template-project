from typing import Any, final

from django.db import transaction
from django.db.models import Count, Prefetch, QuerySet
from django.utils import timezone
from rest_framework.request import Request

from server.apps.company.models import Department
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyResult,
    UserAnswer,
)

QUESTION_ATTR = 'question'
QUESTIONS_ATTR = 'questions'
QUESTION_ID = 'question_id'
QUESTION_TYPE = 'question_type'
TEXT_ATTR = 'text'
ID_ATTR = 'id'
ASC_PARAM = 'asc'
ALL_PARAM = 'all'


@final
class AnswerOptionRepo:
    """Repository for AnswerOption model."""

    def get_all(self) -> QuerySet[AnswerOption]:
        """Returns all answer options from DB."""
        return AnswerOption.objects.select_related(QUESTION_ATTR)

    def get_by_pk(self, pk: int) -> AnswerOption:
        """Returns one answer option from DB by pk."""
        return AnswerOption.objects.select_related(QUESTION_ATTR).get(pk=pk)


@final
class QuestionRepo:
    """Repository for Question model operations."""

    def get_all(self) -> QuerySet[Question]:
        """Return all Question instances from DB."""
        return Question.objects.select_related('survey', 'survey__department')

    def get_by_pk(self, pk: int) -> Question:
        """Return one Question by primary key."""
        return self.get_all().get(pk=pk)

    def update_question(self, question: Question, **kwargs: Any) -> Question:
        """Update an existing question."""
        Question.objects.filter(pk=question.pk).update(**kwargs)
        question.refresh_from_db()
        return question

    def get_modified_questions_queryset(
        self, request: Request
    ) -> QuerySet[Question]:
        """Return optimized and filtered question's queryset."""
        queryset = Question.objects.select_related('survey').prefetch_related(
            Prefetch(
                'answer_options',
                queryset=AnswerOption.objects.only(
                    ID_ATTR, QUESTION_ID, TEXT_ATTR
                ),
            )
        )
        filter_param = request.query_params.get('filter', ALL_PARAM)
        filter_mapping = {
            'favorite': queryset.filter(is_favorite=True),
            'all': queryset,
        }
        queryset = filter_mapping.get(filter_param, queryset)

        order = request.query_params.get('order', ASC_PARAM)
        if order == ASC_PARAM:
            queryset = queryset.order_by(ID_ATTR)
        else:
            queryset = queryset.order_by('-id')

        return queryset


@final
class SurveyRepo:
    """Repository fo Survey model operations."""

    @transaction.atomic
    def create(self, survey_data: dict[str, Any]) -> Survey:
        """Create survey with nested params."""
        department = Department.objects.create(
            **survey_data.pop('department'),
        )
        return Survey.objects.create(
            department=department,
            **survey_data,
        )

    @transaction.atomic
    def add_questions(
        self, survey: Survey, questions_data: list[dict[str, Any]]
    ) -> Survey:
        """Add questions and they answer options for survey instance."""
        for question_data in questions_data:
            answers_data = question_data.pop('answer_options', [])
            question = Question.objects.create(survey=survey, **question_data)
            if answers_data:
                AnswerOption.objects.bulk_create([
                    AnswerOption(question=question, **answer_data)
                    for answer_data in answers_data
                ])
        return survey

    def build_survey_for_create_response(self, survey: Survey) -> Survey:
        """Build survey for create response."""
        return (
            Survey.objects.annotate(
                question_count=Count(QUESTIONS_ATTR, distinct=True),
                finished_count=Count('result', distinct=True),
            )
            .select_related('department')
            .prefetch_related(
                QUESTIONS_ATTR,
                'questions__answer_options',
                'questions__user_answers',
                'questions__user_answers__selected_options',
            )
            .get(pk=survey.pk)
        )

    def get_modified_surveys_queryset(
        self, request: Request
    ) -> QuerySet[Survey]:
        """Return optimize and filtered survey`s queryset."""
        queryset = (
            Survey.objects.annotate(
                question_count=Count(QUESTIONS_ATTR, distinct=True)
            )
            .annotate(finished_count=Count('result', distinct=True))
            .prefetch_related(
                Prefetch(
                    QUESTIONS_ATTR,
                    queryset=Question.objects.only(
                        'id', 'survey_id', 'text', QUESTION_TYPE
                    ),
                ),
                Prefetch(
                    'questions__answer_options',
                    queryset=AnswerOption.objects.only(
                        ID_ATTR, QUESTION_ID, TEXT_ATTR, 'is_correct'
                    ),
                ),
                Prefetch(
                    'questions__user_answers',
                    queryset=(
                        UserAnswer.objects.select_related(
                            'survey_result__user', 'survey_result__survey'
                        ).only(
                            ID_ATTR,
                            QUESTION_ID,
                            'survey_result_id',
                            'text_answer',
                        )
                    ),
                ),
                Prefetch(
                    'result',
                    queryset=SurveyResult.objects.select_related(
                        'user', 'survey'
                    ),
                ),
            )
            .select_related('department')
        )
        queryset = queryset.order_by(
            'start_date'
            if request.query_params.get('order', 'asc') == 'asc'
            else '-start_date'
        )
        now_date = timezone.now().date()
        filter_mapping = {
            'favorite': queryset.filter(is_favorite=True),
            'drafts': queryset.filter(start_date__gt=now_date),
            'finished': queryset.filter(end_date__lte=now_date),
            'archive': queryset.filter(end_date__lt=now_date),
            'all': queryset,
        }
        return filter_mapping[request.query_params.get('filter', ALL_PARAM)]
