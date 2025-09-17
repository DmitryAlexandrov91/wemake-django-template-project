from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users import serializers
from server.apps.users.drf_spectacular_schemas.schema import (
    employee_detail_schema,
)
from server.apps.users.infra.repository import UserRepo
from server.di import resolve

User = get_user_model()


@employee_detail_schema
class EmployeeViewDetail(APIView):
    """Handles operations on a single employee identified by `pk`."""

    def patch(self, request: Request, pk: int) -> Response:
        """Handles employee partial update."""
        employee = resolve(UserRepo).get_employee_with_survey_count(pk)

        serializer = serializers.EmployeeUpdateSerializer(
            employee,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
