from django.contrib import admin

from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyResult,
    UserAnswer,
)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin[Survey]):
    """Admin class for surveys."""

    list_display = (
        'id',  # noqa: WPS226
        'title',
        'start_date',
        'end_date',
    )
    search_fields = ('title',)
    ordering = ('-start_date',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin[Question]):
    """Admin class for questions."""

    list_display = (
        'id',
        'text',  # noqa: WPS226
        'question_type',
        'survey',  # noqa: WPS226
    )
    list_filter = ('question_type', 'survey')
    search_fields = ('text',)
    list_select_related = ('survey',)


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
    list_select_related = ('survey_result', 'question')
