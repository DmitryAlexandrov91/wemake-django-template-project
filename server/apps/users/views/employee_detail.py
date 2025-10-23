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
from server.apps.users.infra.repository import UserRepo, UserRepoSave
from server.apps.users.models import CustomUser
from server.di import resolve

User = get_user_model()


@employee_detail_schema
class EmployeeDetailView(APIView):
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

    def delete(self, request: Request, pk: int) -> Response:
        """Delete employee by primary key."""
        try:
            resolve(UserRepoSave).mark_to_inactivate(pk)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)
