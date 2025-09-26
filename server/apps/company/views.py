from typing import Any, override

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.company.infra.repository import DepartmentRepo
from server.apps.company.models import Department
from server.apps.company.serializers import (
    DepartmentCreateSerializer,
    DepartmentSerializer,
)
from server.di import resolve


class DepartmentViewSet(viewsets.ModelViewSet[Department]):
    """ViewSet for managing departments."""

    serializer_class = DepartmentCreateSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')

    @override
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Create a new department.

        Args:
            request (Request): HTTP request with department_name in body.
            *args (Any): Additional positional arguments (passed to DRF).
            **kwargs (Any): Additional keyword arguments (passed to DRF).

        Returns:
            Response: JSON with created department
                      (id, department_name) and HTTP 201 status.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        department_repo = self.get_repository()
        department: Department = department_repo.create(
            **serializer.validated_data,
        )

        return Response(
            self.get_serializer(department).data,
            status=status.HTTP_201_CREATED,
        )

    @override
    def get_queryset(self) -> QuerySet[Department]:  # noqa: WPS615
        """Get queryset using repo."""
        department_repo = self.get_repository()
        return department_repo.get_all_ordered_by_name()

    @override
    def partial_update(
        self, request: Request, *args: Any, **kwargs: Any
    ) -> Response:
        """Partial update department using repo."""
        department_repo = self.get_repository()
        department = department_repo.get_by_pk(kwargs['pk'])
        serializer = self.get_serializer(
            department, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        upd_department = department_repo.update_department(
            department, **serializer.validated_data
        )
        return Response(
            self.get_serializer(upd_department).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(responses=DepartmentSerializer)
    @override
    def list(self, request: Request) -> Response:
        """Return a list of all departments with employees."""
        serializer = DepartmentSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def get_repository(self) -> DepartmentRepo:
        """Return an instance of DepartmentRepo."""
        return resolve(DepartmentRepo)
