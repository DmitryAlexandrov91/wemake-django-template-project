from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users import serializers
from server.apps.users.infra.repository import UserRepo
from server.di import resolve

User = get_user_model()


class EmployeeListView(APIView):
    """
    GET api/employees?sort=full_name|edited_at&order=asc|desc.

    Returns list of all employees with optional sorting
    and prefetching survey results.
    """

    def get(self, request: Request) -> Response:
        """Get list of employees."""
        sort = request.query_params.get('sort')
        order = request.query_params.get('order', 'asc')
        if sort not in {'full_name', 'edited_at'}:
            sort = None
        if sort and order == 'desc':
            sort = f'-{sort}'
        repo = resolve(UserRepo)
        queryset = repo.get_employees_with_survey_count(sort)
        serializer = serializers.EmployeeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
