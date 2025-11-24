from typing import Any, override

from django.db import transaction
from rest_framework import serializers

from server.apps.company.models import Department
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
SURVEY_FIELD = 'surveys'
ID_FIELD = 'id'
NAME = 'name'
QUESTIONT_FIELD = 'questions'


class QuestionCreateSerializer(serializers.ModelSerializer[Question]):
    """Serializer for creating a new question."""

    surveys = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Survey.objects.all(), required=False
    )

    class Meta:
        model = Question
        fields = (
            ID_FIELD,
            SURVEY_FIELD,
            TEXT_ATTR,
            QUESTION_TYPE_ATTR,
            IS_FAVORITE_ATTR,
            'to_delete',
        )
        read_only_fields = (ID_FIELD,)
        extra_kwargs = {  # noqa: RUF012
            TEXT_ATTR: {'required': True},
            QUESTION_TYPE_ATTR: {'required': True},
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

    id = serializers.IntegerField()

    class Meta:
        model = Question
        fields = (ID_FIELD,)


class SurveyCreateSerializer(serializers.ModelSerializer[Survey]):
    """Serializer for creating survey`s instance."""

    name = serializers.CharField(source='title')
    comment = serializers.CharField(source='description')
    started_at = serializers.DateField(source='start_date')
    finished_at = serializers.DateField(source='end_date')
    questions = QuestionAnswerOptionCreateSerializer(many=True, required=False)
    department_name = serializers.SlugRelatedField(
        slug_field=NAME,
        queryset=Department.objects.all(),
    )
    status = serializers.ChoiceField(
        choices=SurveyStatus.choices,
        required=False,
    )

    class Meta:
        model = Survey
        fields = (
            ID_FIELD,
            NAME,
            'status',
            'comment',
            'started_at',
            'finished_at',
            IS_FAVORITE_ATTR,
            'to_delete',
            QUESTIONT_FIELD,
            'department_name',
        )
        read_only_fields = (ID_FIELD,)

    @override
    def create(self, validated_data: dict[str, Any]) -> Survey:
        """Custom create for saving nested objects."""
        with transaction.atomic():
            return resolve(SurveyRepo).create_survey_with_questions(
                validated_data
            )


class SurveyUpdateSerializer(serializers.ModelSerializer[Survey]):
    """Serializer for updating survey`s instance."""

    name = serializers.CharField(source='title', required=False)
    comment = serializers.CharField(source='description', required=False)
    started_at = serializers.DateField(source='start_date', required=False)
    finished_at = serializers.DateField(source='end_date', required=False)
    department_name = serializers.SlugRelatedField(
        slug_field=NAME,
        queryset=Department.objects.all().select_related(),
        required=False,
    )
    status = serializers.ChoiceField(
        choices=SurveyStatus.choices,
        required=False,
    )
    questions = QuestionAnswerOptionCreateSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = (
            ID_FIELD,
            NAME,
            'comment',
            'started_at',
            'finished_at',
            IS_FAVORITE_ATTR,
            'to_delete',
            'department_name',
            'status',
            QUESTIONT_FIELD,
        )

    @override
    def update(
        self, instance: Survey, validated_data: dict[str, Any]
    ) -> Survey:
        """Use repo for update operation with nested relations."""
        return resolve(SurveyRepo).update_survey(instance, **validated_data)

    def validate_questions(self, questions: Any) -> Any:
        """Only drafts can have questions changed."""
        if self.instance and self.instance.status != SurveyStatus.DRAFT:
            raise serializers.ValidationError('Можно менять только черновикам.')
        return questions

    def validate_finished_at(self, end_date: Any) -> Any:
        """End date editable only for draft/active surveys."""
        if self.instance and self.instance.status not in {
            SurveyStatus.DRAFT,
            SurveyStatus.ACTIVE,
        }:
            raise serializers.ValidationError(
                'Дату окончания можно изменить '
                'опросам чей статус: активный или черновик'
            )
        return end_date

    def validate_status(self, status: Any) -> Any:
        """Cannot revert active/completed survey back to draft."""
        if (
            self.instance
            and status == SurveyStatus.DRAFT
            and self.instance.status
            in {SurveyStatus.ACTIVE, SurveyStatus.COMPLETED}
        ):
            raise serializers.ValidationError(
                'Невозможно поменять статус активного '
                'или завершенного опроса на черновик'
            )
        return status
