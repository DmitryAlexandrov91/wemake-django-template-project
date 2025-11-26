from datetime import timedelta
from typing import Any, final

from django.db import models, transaction
from django.utils import timezone
from rest_framework.request import Request

from server.apps.surveys.choices import SurveyBotState, SurveyStatus
from server.apps.surveys.models import (
    AnswerOption,
    Question,
    StatisticSettings,
    Survey,
    SurveyQuestion,
    SurveyResult,
    UserAnswer,
    UserStatistics,
)
from server.apps.users.models import CustomUser

QUESTION_ATTR = 'question'
QUESTIONS_ATTR = 'questions'
QUESTION_ID = 'question_id'
QUESTION_TYPE = 'question_type'
TEXT_ATTR = 'text'
ID_ATTR = 'id'
ALL_PARAM = 'all'
DEPARTMENT = 'department'
SURVEY_ATTR = 'surveys'
SURVYE_FIELD = 'survey'


@final
class AnswerOptionRepo:
    """Repository for AnswerOption model."""

    def get_all(self) -> models.QuerySet[AnswerOption]:
        """Returns all answer options from DB."""
        return AnswerOption.objects.select_related(QUESTION_ATTR)

    def get_by_pk(self, pk: int) -> AnswerOption:
        """Returns one answer option from DB by pk."""
        return AnswerOption.objects.select_related(QUESTION_ATTR).get(pk=pk)

    def get_by_question(
        self, question: Question | None
    ) -> models.QuerySet[AnswerOption]:
        """Returns all answer options by question."""
        return self.get_all().filter(question=question)


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

        if order_param == 'asc':
            queryset = queryset.order_by(ID_ATTR)
        else:
            queryset = queryset.order_by(f'-{ID_ATTR}')

        return queryset

    def get_all_to_delete_ids(self) -> list[int]:
        """Returns all the questions to delete."""
        return list(
            Question.objects.filter(to_delete=True).values_list(
                ID_ATTR, flat=True
            )
        )

    def delete(self, pk: int) -> None:
        """Delete an existing question."""
        question = Question.objects.get(pk=pk)
        question.delete()

    def survey_assigned_to_question(self, question: Question) -> bool:
        """Reports there is s survey assigned to the question."""
        return question.surveys.exists()


@final
class SurveyRepo:  # noqa: WPS214
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

        self._add_questions_to_survey(survey, questions_data)

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
                        ID_ATTR, 'text', QUESTION_TYPE, 'to_delete'
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
        search_param = request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(title__icontains=search_param)

        queryset = queryset.order_by(
            '-start_date',
            '-id'
            if request.query_params.get('order', 'desc') == 'desc'
            else 'start_date',
            'id',
        )

        # this filter mapping is for compatability with frontend queries
        # using ?filter=XXXX param. Now Frontend works with native DRF ?status=X
        # this also used in tests
        now_date = timezone.now().date()
        filter_mapping = {
            'favorite': queryset.filter(is_favorite=True),
            'drafts': queryset.filter(status=SurveyStatus.DRAFT),
            'finished': queryset.filter(
                models.Q(end_date__lte=now_date)
                | models.Q(status=SurveyStatus.COMPLETED)
            ),
            'archive': queryset.filter(status=SurveyStatus.ARCHIVED),
            'all': queryset,
        }
        return filter_mapping[request.query_params.get('filter', ALL_PARAM)]

    def update_survey(self, survey: Survey, **kwargs: Any) -> Survey:
        """Update survey."""
        department = kwargs.pop('department_name', None)
        questions_data = kwargs.pop('questions', None)

        mapped_data = {
            key: field_value
            for key, field_value in kwargs.items()
            if field_value is not None
        }

        if department:
            mapped_data['department'] = department

        Survey.objects.filter(pk=survey.pk).update(**mapped_data)

        if questions_data:
            SurveyQuestion.objects.filter(survey=survey).delete()
            self._add_questions_to_survey(survey, questions_data)

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

    def get_active_surveys_for_user(
        self, user: CustomUser
    ) -> models.QuerySet[Survey]:
        """Returns all active surveys for user."""
        now_date = timezone.now().date()
        return Survey.objects.filter(
            department=user.department,
            start_date__lte=now_date,
            status=SurveyStatus.ACTIVE,
        ).filter(
            models.Q(end_date__gte=now_date) | models.Q(end_date__isnull=True)
        )

    def get_active_survey_for_user(self, user: CustomUser) -> Survey:
        """Returns the last active survey for the user, if any."""
        return self.get_active_surveys_for_user(user=user).latest('start_date')

    def get_by_pk(self, pk: int) -> Survey:
        """Returns single Survey obj by pk."""
        return Survey.objects.get(pk=pk)

    def get_survey_recipients(
        self,
        survey: Survey,
    ) -> models.QuerySet[CustomUser]:
        """Returns users to participate in the survey."""
        return survey.department.users.all()

    def get_active_survey_for_user_by_id(
        self, user: CustomUser, survey_id: int
    ) -> Survey:
        """Returns survey by id."""
        now_date = timezone.now().date()
        return (
            Survey.objects.filter(
                department=user.department,
                start_date__lte=now_date,
                status=SurveyStatus.ACTIVE,
            )
            .exclude(end_date__lt=now_date, end_date__isnull=False)
            .get(pk=survey_id)
        )

    def _add_questions_to_survey(
        self, survey: Survey, questions_data: list[dict[str, int]]
    ) -> None:
        """Add questions to a survey."""
        for question_data in questions_data:
            question = Question.objects.get(id=question_data[ID_ATTR])
            SurveyQuestion.objects.create(survey=survey, question=question)


@final
class SurveySaveRepo:
    """Repository fot survey processing."""

    def get_by_pk(self, pk: int) -> Survey:
        """Returns one survey from DB by pk."""
        return Survey.objects.get(pk=pk)

    def delete(self, pk: int) -> None:
        """Delete an existing survey."""
        survey = Survey.objects.get(pk=pk)
        survey.delete()

    def get_all_to_delete_ids(self) -> list[int]:
        """Returns all the surveys to delete."""
        return list(
            Survey.objects.filter(to_delete=True).values_list(
                ID_ATTR, flat=True
            )
        )

    def get_all_expired_ids(self) -> list[int]:
        """Returns all the surveys to mark completed."""
        now_date = timezone.now().date()
        return list(
            Survey.objects.filter(
                status=SurveyStatus.ACTIVE, end_date__lt=now_date
            ).values_list(ID_ATTR, flat=True)
        )


@final
class SurveyResultRepo:
    """Repository for survey results."""

    def get_by_pk(self, pk: int) -> SurveyResult:
        """Returns one survey result from DB by pk."""
        return SurveyResult.objects.get(pk=pk)

    def get_or_create_user_survey_res(
        self, user: CustomUser, survey: Survey
    ) -> SurveyResult:
        """Finds or creates SurveyResult object for the user and survey."""
        first_question = (
            SurveyQuestion.objects.filter(survey=survey).earliest('pk').question
        )
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

    def get_completed_surveys(
        self, user: CustomUser
    ) -> models.QuerySet[SurveyResult]:
        """Return all completed survey results for the given user."""
        return (
            SurveyResult.objects.filter(
                user=user,
                bot_state=SurveyBotState.COMPLETED,
            )
            .select_related(SURVYE_FIELD)
            .prefetch_related('user_answers__question')
        )


@final
class UserAnswerRepo:
    """Repository for user answers."""

    def get_answers_by_survey_result(
        self,
        survey_result: SurveyResult,
    ) -> models.QuerySet[UserAnswer]:
        """Returns all answers for current survey result."""
        return (
            UserAnswer.objects.filter(survey_result=survey_result)
            .select_related('survey_result', 'question')
            .prefetch_related('selected_options')
            .order_by('pk')
        )

    def get_user_survey_results_aggr(
        self, user: CustomUser, limit: int
    ) -> tuple[timedelta, int]:
        """Returns the aggregated responded questions and time for user."""
        res = (
            user.survey_result.filter(
                current_question__isnull=True, completed_questions__gt=0
            )
            .order_by('-updated_at')[:limit]
            .aggregate(
                total_time=models.Sum(
                    models.ExpressionWrapper(
                        models.F('updated_at') - models.F('started_at'),
                        output_field=models.DurationField(),
                    )
                ),
                total_questions=models.Sum('completed_questions'),
            )
        )
        return res['total_time'], res['total_questions']

    def edit_user_answer(
        self, answer_id: int, new_text_answer: str
    ) -> UserAnswer:
        """Edit user answer text."""
        instance = UserAnswer.objects.get(pk=answer_id)
        instance.text_answer = new_text_answer
        instance.save()
        return instance

    @transaction.atomic
    def save_user_answer(
        self,
        survey_result: SurveyResult,
        question: Question,
        text_answer: str,
        selected_options: list[AnswerOption] | None = None,
    ) -> UserAnswer:
        """Create user answer instance."""
        user_answer = UserAnswer.objects.create(
            survey_result=survey_result,
            question=question,
            text_answer=text_answer,
        )

        if selected_options:
            user_answer.selected_options.set(selected_options)

        return user_answer


@final
class UserStatisticsRepo:
    """Repository for user statistics."""

    def get_stat_settings(self) -> StatisticSettings:
        """Getting statistics settings."""
        stat_settings, _ = StatisticSettings.objects.get_or_create(pk=1)
        return stat_settings

    def get_statistics(self, user: CustomUser) -> UserStatistics:
        """Getting statistics for the user."""
        user_statistics, _ = UserStatistics.objects.get_or_create(user=user)
        return user_statistics

    def save_statistics(
        self, user: CustomUser, avg_answer_sec: int
    ) -> UserStatistics:
        """Save user statistics."""
        instance, _ = UserStatistics.objects.get_or_create(user=user)
        instance.average_answer_sec = avg_answer_sec
        instance.save()
        return instance
