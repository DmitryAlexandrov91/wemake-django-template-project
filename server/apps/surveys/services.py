from django.db.models import Count, Prefetch, QuerySet
from django.utils import timezone
from rest_framework.request import Request

from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyResult,
    UserAnswer,
)


def get_modified_surveys_queryset(request: Request) -> QuerySet[Survey]:
    """Return optimize and filtered survey`s queryset."""
    queryset = (
        Survey.objects.annotate(
            question_count=Count('questions', distinct=True)
        )
        .annotate(finished_count=Count('result', distinct=True))
        .prefetch_related(
            Prefetch(
                'questions',
                queryset=Question.objects.only(
                    'id', 'survey_id', 'text', 'question_type'
                ),
            ),
            Prefetch(
                'questions__answer_options',
                queryset=AnswerOption.objects.only(
                    'id', 'question_id', 'text', 'is_correct'
                ),
            ),
            Prefetch(
                'questions__user_answers',
                queryset=(
                    UserAnswer.objects.select_related(
                        'survey_result__user', 'survey_result__survey'
                    ).only(
                        'id',
                        'question_id',
                        'survey_result_id',
                        'text_answer',
                    )
                ),
            ),
            Prefetch(
                'result',
                queryset=SurveyResult.objects.select_related('user', 'survey'),
            ),
        )
        .select_related('department')
    )
    order = request.query_params.get('order', 'asc')
    queryset = queryset.order_by(
        'start_date' if order == 'asc' else '-start_date'
    )
    filter_param = request.query_params.get('filter', 'all')
    now_date = timezone.now().date()
    if filter_param == 'favorite':
        queryset = queryset.filter(is_favorite=True)
    if filter_param == 'drafts':
        queryset = queryset.filter(start_date__gt=now_date)
    if filter_param == 'finished':
        queryset = queryset.filter(end_date__lte=now_date)
    if filter_param == 'archive':
        queryset = queryset.filter(end_date__lt=now_date)
    return queryset
