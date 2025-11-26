from typing import Any, override

from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from server.apps.company.infra.repository import DepartmentRepo
from server.apps.company.models import Department
from server.apps.company.paginators import DepartmentPaginator
from server.apps.company.schemas import department_viewset_schema
from server.apps.company.serializers import (
    DepartmentCreateSerializer,
    DepartmentSerializer,
)
from server.di import resolve


@department_viewset_schema
class DepartmentViewSet(viewsets.ModelViewSet[Department]):
    """ViewSet for managing departments."""

    serializer_class = DepartmentCreateSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = DepartmentPaginator
    lookup_value_regex = r'\d+'

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

    @override
    def list(self, request: Request) -> Response:
        """Return a list of all departments with employees."""
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = DepartmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = DepartmentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_repository(self) -> DepartmentRepo:
        """Return an instance of DepartmentRepo."""
        return resolve(DepartmentRepo)

    @override
    def destroy(self, request: Request, pk: int) -> Response:
        """Mark empty department for deletion by primary key."""
        repo = resolve(DepartmentRepo)
        department = repo.get_by_pk(pk)
        if repo.active_users_in_department(department):
            return Response(
                data={'error': 'User(s) in department.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if repo.surveys_in_department(department):
            return Response(
                data={'error': 'Survey(s) assigned to the department.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        repo.update_department(department=department, to_delete=True)
        return Response(status=status.HTTP_200_OK)
