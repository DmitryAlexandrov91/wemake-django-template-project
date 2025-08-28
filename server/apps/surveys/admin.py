from django.contrib import admin

from server.apps.surveys.models import AnswerOption, Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin[Question]):
    """Admin class for questions."""

    list_display = (
        'id',
        'text',
        'question_type',
    )


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin[AnswerOption]):
    """Admin class for answer options."""

    list_display = (
        'id',
        'text',
        'question__text',
    )
    list_select_related = ('question',)
