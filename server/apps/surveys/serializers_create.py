from typing import Any, override

from rest_framework import serializers

from server.apps.company.serializers import DepartmentCreateSerializer
from server.apps.surveys.choices import SurveyStatus
from server.apps.surveys.infra.repository import SurveyRepo
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
)
from server.di import resolve

ATTR_PK = 'pk'
TEXT_ATTR = 'text'
QUESTION_TYPE_ATTR = 'question_type'
IS_FAVORITE_ATTR = 'is_favorite'
SURVEY_FIELD = 'survey'
ID_FIELD = 'id'


class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    """Serializer for creating a new question."""

    class Meta:
        model = Question
        fields = (
            ID_FIELD,
            SURVEY_FIELD,
            TEXT_ATTR,
            QUESTION_TYPE_ATTR,
            IS_FAVORITE_ATTR,
        )
        read_only_fields = (ID_FIELD,)
        extra_kwargs = {  # noqa: RUF012
            TEXT_ATTR: {'required': True},
            QUESTION_TYPE_ATTR: {'required': True},
            SURVEY_FIELD: {'required': True},
        }


class AnswerOptionCreateSerializer(serializers.ModelSerializer[AnswerOption]):
    """Serializer for creating UserOption instance."""

    class Meta:
        model = AnswerOption
        fields = (TEXT_ATTR, 'is_correct')


class QuestionAnswerOptionCreateSerializer(
    serializers.ModelSerializer[Question],
):
    """Serializer for creating Question instance."""

    type = serializers.CharField(source=QUESTION_TYPE_ATTR)
    answers = AnswerOptionCreateSerializer(
        source='answer_options', many=True, required=False
    )

    class Meta:
        model = Question
        fields = (TEXT_ATTR, 'type', IS_FAVORITE_ATTR, 'answers')


class SurveyCreateSerializer(serializers.ModelSerializer[Survey]):
    """Serializer for creating survey`s instance."""

    name = serializers.CharField(source='title')
    comment = serializers.CharField(source='description')
    started_at = serializers.DateField(source='start_date')
    finished_at = serializers.DateField(source='end_date')
    questions = QuestionAnswerOptionCreateSerializer(many=True, required=False)
    department = DepartmentCreateSerializer()
    status = serializers.ChoiceField(
        choices=SurveyStatus.choices,
        required=False,
    )

    class Meta:
        model = Survey
        fields = (
            ID_FIELD,
            'name',
            'status',
            'comment',
            'started_at',
            'finished_at',
            IS_FAVORITE_ATTR,
            'questions',
            'department',
        )
        read_only_fields = (ID_FIELD,)

    @override
    def create(self, validated_data: dict[str, Any]) -> Survey:
        """Custom create for saving nested objects."""
        repo = resolve(SurveyRepo)
        questions = validated_data.pop('questions', [])
        survey = repo.create(validated_data)
        return repo.add_questions(survey, questions)


class SurveyUpdateSerializer(serializers.ModelSerializer[Survey]):
    """Serializer for updating survey`s instance."""

    name = serializers.CharField(source='title', required=False)
    comment = serializers.CharField(source='description', required=False)
    started_at = serializers.DateField(source='start_date', required=False)
    finished_at = serializers.DateField(source='end_date', required=False)
    department = DepartmentCreateSerializer(required=False)

    class Meta:
        model = Survey
        fields = (
            ID_FIELD,
            'name',
            'comment',
            'started_at',
            'finished_at',
            IS_FAVORITE_ATTR,
            'department',
        )

    @override
    def update(
        self, instance: Survey, validated_data: dict[str, Any]
    ) -> Survey:
        """Use repo for update operation with nested relations."""
        repo = resolve(SurveyRepo)
        return repo.update_survey(instance, **validated_data)
