from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers, status

from server.apps.users.serializers import (
    EmployeeCreateSerializer,
    EmployeeResponseSerializer,
    EmployeeSerializer,
    EmployeeUpdateSerializer,
)

password_recovery_schema = extend_schema_view(
    post=extend_schema(
        request=inline_serializer(
            name='PasswordRecoveryRequest',
            fields={'email': serializers.EmailField()},
        ),
        responses={status.HTTP_200_OK: None},
    )
)

employee_view_schema = extend_schema_view(
    get=extend_schema(
        operation_id='employee_list_all',
        parameters=[
            OpenApiParameter(
                name='sort',
                required=False,
                type=str,
                enum=['full_name', 'edited_at'],
            ),
            OpenApiParameter(
                name='order',
                required=False,
                type=str,
                enum=['asc', 'desc'],
                default='asc',
            ),
        ],
        responses=EmployeeSerializer(many=True),
    ),
    post=extend_schema(
        operation_id='employee_create',
        request=EmployeeCreateSerializer,
        responses={
            status.HTTP_201_CREATED: EmployeeSerializer,
        },
    ),
)

employee_detail_schema = extend_schema_view(
    patch=extend_schema(
        operation_id='employee_partial_update',
        request=EmployeeUpdateSerializer,
        responses={
            status.HTTP_202_ACCEPTED: EmployeeResponseSerializer,
        },
    ),
    delete=extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: None,
        },
    ),
)
