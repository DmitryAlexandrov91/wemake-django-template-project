from typing import Any, final

from django.db import models, transaction
from django.utils import timezone
from rest_framework.request import Request

from server.apps.surveys.models import (
    AnswerOption,
    Question,
    Survey,
    SurveyQuestion,
    SurveyResult,
    UserAnswer,
)
from server.apps.users.models import CustomUser

QUESTION_ATTR = 'question'
QUESTIONS_ATTR = 'questions'
QUESTION_ID = 'question_id'
QUESTION_TYPE = 'question_type'
TEXT_ATTR = 'text'
ID_ATTR = 'id'
ASC_PARAM = 'asc'
ALL_PARAM = 'all'
DEPARTMENT = 'department'
SURVEY_ATTR = 'surveys'


@final
class AnswerOptionRepo:
    """Repository for AnswerOption model."""

    def get_all(self) -> models.QuerySet[AnswerOption]:
        """Returns all answer options from DB."""
        return AnswerOption.objects.select_related(QUESTION_ATTR)

    def get_by_pk(self, pk: int) -> AnswerOption:
        """Returns one answer option from DB by pk."""
        return AnswerOption.objects.select_related(QUESTION_ATTR).get(pk=pk)


@final
class QuestionRepo:
    """Repository for Question model operations."""

    def get_all(self) -> models.QuerySet[Question]:
        """Return all Question instances from DB."""
        return Question.objects.prefetch_related(
            SURVEY_ATTR, 'surveys__department'
        )

    def get_by_pk(self, pk: int) -> Question:
        """Return one Question by primary key."""
        return self.get_all().get(pk=pk)

    def update_question(self, question: Question, **kwargs: Any) -> Any:
        """Update an existing question."""
        surveys = kwargs.pop('surveys', None)
        for attr, value_data in kwargs.items():
            setattr(question, attr, value_data)
        question.save()
        question.refresh_from_db()
        if surveys is not None:
            question.surveys.set(surveys)
        return question

    def get_modified_questions_queryset(
        self,
        filter_param: str,
        order_param: str,
        search_param: str | None = None,
    ) -> models.QuerySet[Question]:
        """Return optimized and filtered question's queryset."""
        queryset = Question.objects.prefetch_related(
            models.Prefetch(
                'answer_options',
                queryset=AnswerOption.objects.only(
                    ID_ATTR, QUESTION_ID, TEXT_ATTR
                ),
            ),
            SURVEY_ATTR,
        )

        if search_param:
            queryset = queryset.filter(text__icontains=search_param)

        filter_mapping = {
            'favorite': queryset.filter(is_favorite=True),
            'all': queryset,
        }
        queryset = filter_mapping.get(filter_param, queryset)

        if order_param == ASC_PARAM:
            queryset = queryset.order_by(ID_ATTR)
        else:
            queryset = queryset.order_by(f'-{ID_ATTR}')

        return queryset

    def delete(self, pk: int) -> None:
        """Delete an existing question."""
        instance = Question.objects.get(pk=pk)
        instance.delete()


@final
class SurveyRepo:
    """Repository fo Survey model operations."""

    @transaction.atomic
    def create_survey_with_questions(
        self, survey_data: dict[str, Any]
    ) -> Survey:
        """Create survey with all questions in one transaction."""
        questions_data = survey_data.pop('questions', [])
        survey = Survey.objects.create(
            department=survey_data.pop('department_name'), **survey_data
        )

        for question_data in questions_data:
            answers_data = question_data.pop('answers', [])
            question = Question.objects.create(**question_data)

            SurveyQuestion.objects.create(survey=survey, question=question)

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
                question_count=models.Count(QUESTIONS_ATTR, distinct=True),
                finished_count=models.Count('result', distinct=True),
            )
            .select_related(DEPARTMENT)
            .prefetch_related(
                QUESTIONS_ATTR,
                'questions__answer_options',
                'questions__user_answers',
                'questions__user_answers__selected_options',
                'questions__surveys',
            )
            .get(pk=survey.pk)
        )

    def get_modified_surveys_queryset(
        self, request: Request
    ) -> models.QuerySet[Survey]:
        """Return optimize and filtered survey`s queryset."""
        queryset = (
            Survey.objects.annotate(
                question_count=models.Count(QUESTIONS_ATTR, distinct=True)
            )
            .annotate(finished_count=models.Count('result', distinct=True))
            .prefetch_related(
                models.Prefetch(
                    QUESTIONS_ATTR,
                    queryset=Question.objects.only(
                        'id', 'text', QUESTION_TYPE
                    ).prefetch_related('surveys'),
                ),
                models.Prefetch(
                    'questions__answer_options',
                    queryset=AnswerOption.objects.only(
                        ID_ATTR, QUESTION_ID, TEXT_ATTR, 'is_correct'
                    ),
                ),
                models.Prefetch(
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
                models.Prefetch(
                    'result',
                    queryset=SurveyResult.objects.select_related(
                        'user', 'survey'
                    ),
                ),
            )
            .select_related(DEPARTMENT)
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

    def update_survey(self, survey: Survey, **kwargs: Any) -> Survey:
        """Update survey."""
        department = kwargs.pop('department_name', None)

        mapped_data = {
            key: field_value
            for key, field_value in kwargs.items()
            if field_value is not None
        }

        if department:
            mapped_data['department'] = department

        Survey.objects.filter(pk=survey.pk).update(**mapped_data)
        survey.refresh_from_db()

        return survey

    def get_results(self, survey_id: int) -> models.QuerySet[SurveyResult]:
        """Get all SurveyResults objects with their answers by survey_id."""
        return (
            Survey.objects.get(pk=survey_id)
            .result.select_related('user', 'survey')
            .prefetch_related(
                models.Prefetch(
                    'user_answers',
                    queryset=UserAnswer.objects.select_related(
                        QUESTION_ATTR,
                    ).only(ID_ATTR, 'text_answer', 'question_id'),
                ),
                models.Prefetch(
                    'user_answers__selected_options',
                    queryset=AnswerOption.objects.select_related(
                        'question',
                    ).only(ID_ATTR, TEXT_ATTR, 'is_correct', 'question_id'),
                ),
            )
        )

    def get_active_survey_for_user(self, user: CustomUser) -> Survey:
        """Returns the only active survey for the user, if any."""
        now_date = timezone.now().date()
        return (
            Survey.objects.filter(
                department=user.department, start_date__lte=now_date
            )
            .filter(
                models.Q(end_date__gte=now_date)
                | models.Q(end_date__isnull=True)
            )
            .latest('start_date')
        )


@final
class SurveyResultRepo:
    """Repository for survey results."""

    def get_or_create_user_survey_res(
        self, user: CustomUser, survey: Survey
    ) -> SurveyResult:
        """Finds or creates SurveyResult object for the user and survey."""
        first_question = survey.questions.earliest('pk')
        user_survey_result, _ = SurveyResult.objects.get_or_create(
            user=user,
            survey=survey,
            defaults={
                'current_question': first_question,
            },
        )
        return user_survey_result

    @transaction.atomic
    def save_answer(
        self,
        survey_result: SurveyResult,
        text_answer: str | None = None,
        selected_options: list[AnswerOption] | None = None,
    ) -> UserAnswer:
        """Save user's answer for the current question."""
        if not survey_result.current_question:
            raise ValueError('Survey has no current question to answer.')

        user_answer = UserAnswer.objects.create(
            survey_result=survey_result,
            question=survey_result.current_question,
            text_answer=text_answer or '',
        )

        if selected_options:
            user_answer.selected_options.set(selected_options)

        return user_answer
