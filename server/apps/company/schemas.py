from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)

from server.apps.company.serializers import DepartmentSerializer

department_viewset_schema = extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='per_page',
                required=False,
                type=OpenApiTypes.STR,
                description=(
                    "Number of items per page or 'all' to return all objects"
                ),
            ),
        ],
        responses=DepartmentSerializer(many=True),
    ),
)
