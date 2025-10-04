from rest_framework import serializers

from server.apps.surveys.models import SurveyResult


class SurveyTimeReportSerializer(serializers.ModelSerializer[SurveyResult]):
    """How much did it take for the employee to complete the survey."""

    employee = serializers.IntegerField(source='user.id', read_only=True)
    survey_sec = serializers.SerializerMethodField()

    class Meta:
        model = SurveyResult
        fields = ('employee', 'survey_sec')

    def get_survey_sec(self, survey_res: SurveyResult) -> int:  # noqa: WPS615
        """Calculate the time the user spent for the survey."""
        return int(
            (survey_res.updated_at - survey_res.started_at).total_seconds()
        )
