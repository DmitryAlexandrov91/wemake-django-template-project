from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)

question_viewset_schema = extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='filter',
                required=False,
                type=str,
                enum=['favorite', 'all'],
                default='all',
            ),
            OpenApiParameter(
                name='order',
                required=False,
                type=str,
                enum=['asc', 'desc'],
                default='asc',
            ),
        ],
    ),
)
