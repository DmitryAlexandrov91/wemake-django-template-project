from typing import override

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from server.apps.surveys.infra.repository import QuestionRepo
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyQuestion,
    SurveyResult,
    UserAnswer,
)


class QuestionInline(admin.TabularInline[SurveyQuestion, Survey]):
    """Question in Surveys."""

    model = SurveyQuestion
    extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin[Survey]):
    """Admin class for surveys."""

    list_display = (
        'id',  # noqa: WPS226
        'title',
        'start_date',
        'end_date',
    )
    search_fields = ('title', 'id')
    ordering = ('-start_date',)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin[Question]):
    """Admin class for questions."""

    list_display = (
        'id',
        'text',  # noqa: WPS226
        'question_type',
        'get_surveys',  # noqa: WPS226
    )
    list_filter = ('question_type', 'surveys')
    search_fields = ('text',)

    @admin.display(description='Surveys')
    def get_surveys(self, question: Question) -> str:
        """Get surveys."""
        repo = QuestionRepo()
        question = repo.get_by_pk(question.pk)  # with prefetch surveys
        return ', '.join(survey.title for survey in question.surveys.all())

    @override
    def get_queryset(self, request: HttpRequest) -> QuerySet[Question]:
        """Get queryset with prefetch."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('surveys')


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin[AnswerOption]):
    """Admin class for answer options."""

    list_display = (
        'id',
        'text',
        'question',  # noqa: WPS226
    )
    list_select_related = ('question',)
    search_fields = ('text', 'question__text')


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin[SurveyResult]):
    """Admin class for survey result."""

    list_display = (
        'id',
        'user',
        'survey',
    )
    list_filter = ('survey',)
    search_fields = (
        'user__username',
        'user__email',
        'survey__title',
    )
    list_select_related = ('user', 'survey')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin[UserAnswer]):
    """Admin class for user answer."""

    list_display = (
        'survey_result',
        'question',
    )
    list_select_related = (
        'survey_result__user',
        'survey_result__survey',
        'question',
    )
