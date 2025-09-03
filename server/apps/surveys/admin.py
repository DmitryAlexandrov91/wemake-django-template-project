from django.contrib import admin

from server.apps.surveys.models import AnswerOption, Question, Survey


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin[Survey]):
    """Admin class for surveys."""

    list_display = (
        'id',
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
        'survey',
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
        'question',
    )
    list_select_related = ('question',)
    search_fields = ('text', 'question__text')
