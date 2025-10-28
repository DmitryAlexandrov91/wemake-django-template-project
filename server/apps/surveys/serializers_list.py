from django.db.models import Model
from rest_framework import serializers

from server.apps.company.models import Department
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    UserAnswer,
)
from server.apps.surveys.serializers_report import SurveyTimeReportSerializer
from server.apps.users.serializers import UserShortSerializer

ATTR_PK = 'pk'
TEXT_ATTR = 'text'
QUESTION_TYPE_ATTR = 'question_type'
IS_FAVORITE_ATTR = 'is_favorite'


class SerializerIDFieldMixin[ModelT: Model](
    serializers.ModelSerializer[ModelT],
):
    """Serializer mixin for adding id field."""

    id = serializers.IntegerField(source=ATTR_PK, read_only=True)

    class Meta:
        abstract = True


class UserAnswersListSerializer(SerializerIDFieldMixin[UserAnswer]):
    """Serializer for Answer model."""

    id = serializers.IntegerField(source=ATTR_PK, read_only=True)
    result = serializers.SerializerMethodField()  # noqa: WPS110
    employer = UserShortSerializer(source='survey_result.user')

    class Meta:
        model = UserAnswer
        fields = ('id', 'result', 'employer')  # noqa: WPS226

    def get_result(self, user_answer: UserAnswer) -> int | str | list[str]:  # noqa: WPS615
        """Return result of user`s passing of survey."""
        if user_answer.text_answer:
            return user_answer.text_answer
        return [
            selected_option.text
            for selected_option in user_answer.selected_options.all()
        ]


class AnswerOptionListSerializer(serializers.ModelSerializer[AnswerOption]):
    """Serializer for display AnswerOption instances."""

    class Meta:
        model = AnswerOption
        fields = ('id', TEXT_ATTR, 'is_correct')


class QuestionListSerializer(SerializerIDFieldMixin[Question]):
    """Serializer for Question model."""

    id = serializers.IntegerField(source=ATTR_PK, read_only=True)
    text = serializers.CharField()
    type = serializers.CharField(source=QUESTION_TYPE_ATTR)
    user_answers = UserAnswersListSerializer(many=True)
    answer_options = AnswerOptionListSerializer(many=True)
    surveys = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Survey.objects.all()
    )

    class Meta:
        model = Question
        fields = (
            'id',
            TEXT_ATTR,
            'type',
            'to_delete',
            'user_answers',
            'answer_options',
            'surveys',
        )


class QuestionShortSerializer(SerializerIDFieldMixin[Question]):
    """Short serializer for Question model."""

    text = serializers.CharField()
    question_type = serializers.CharField()
    is_favorite = serializers.BooleanField()
    surveys = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Survey.objects.all()
    )

    class Meta:
        model = Question
        fields = (
            'id',
            TEXT_ATTR,
            QUESTION_TYPE_ATTR,
            'is_favorite',
            'to_delete',
            'surveys',
        )


class DepartmentListSerializer(SerializerIDFieldMixin[Department]):
    """Serializer for Department model."""

    id = serializers.IntegerField(source=ATTR_PK, read_only=True)
    name = serializers.CharField()

    class Meta:
        model = Department
        fields = ('id', 'name')


class SurveyListSerializer(SerializerIDFieldMixin[Survey]):
    """Serializer for Survey model."""

    id = serializers.IntegerField(source=ATTR_PK, read_only=True)
    name = serializers.CharField(source='title')
    comment = serializers.CharField(source='description')
    started_at = serializers.DateField(source='start_date')
    finished_at = serializers.DateField(source='end_date')
    is_favorite = serializers.BooleanField()
    question_count = serializers.IntegerField(read_only=True)
    finished_count = serializers.IntegerField(read_only=True)
    questions = QuestionListSerializer(many=True)
    department = DepartmentListSerializer()
    employees = SurveyTimeReportSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = (
            'id',
            'name',
            'comment',
            'started_at',
            'finished_at',
            IS_FAVORITE_ATTR,
            'to_delete',
            'question_count',
            'finished_count',
            'questions',
            'department',
            'status',
            'employees',
        )
