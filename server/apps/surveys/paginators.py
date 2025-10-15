from typing import Any, override

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

TYPE = 'type'
EXAMPLE = 'example'
TYPE_INT = 'integer'
TYPE_BOOL = 'boolen'
PAGINATED_FIELD_DATA = 'data'
PAGINATED_FIELD_PAGE = 'page'
PAGINATED_FIELD_PER_PAGE = 'per_page'
PAGINATED_FIELD_TOTAL = 'total'
PAGINATED_FIELD_NUM_PAGE = 'num_pages'
PAGINATED_FIELD_HAS_NEXT = 'has_next'
PAGINATED_FIELD_HAS_PREVIOUS = 'has_previous'


class CustomPaginator(PageNumberPagination):
    """Custom paginator."""

    page_size_query_param = PAGINATED_FIELD_PER_PAGE

    @override
    def get_paginated_response(
        self, paginated_data: list[dict[str, int]]
    ) -> Response:
        """Return custom paginators`s response body."""
        page = getattr(self, PAGINATED_FIELD_PAGE, None)
        if page is None:
            return Response({PAGINATED_FIELD_DATA: paginated_data})
        return Response({
            PAGINATED_FIELD_DATA: paginated_data,
            PAGINATED_FIELD_PAGE: page.number,
            PAGINATED_FIELD_PER_PAGE: page.paginator.per_page,
            PAGINATED_FIELD_TOTAL: page.paginator.count,
            PAGINATED_FIELD_NUM_PAGE: page.paginator.num_pages,
            PAGINATED_FIELD_HAS_NEXT: page.has_next(),
            PAGINATED_FIELD_HAS_PREVIOUS: page.has_previous(),
        })

    @override
    def get_paginated_response_schema(
        self,
        schema: Any,
    ) -> dict[str, Any]:
        """Return schema for a paginated response."""
        return {
            TYPE: 'object',
            'required': [
                PAGINATED_FIELD_DATA,
                PAGINATED_FIELD_PAGE,
                PAGINATED_FIELD_PER_PAGE,
                PAGINATED_FIELD_TOTAL,
                PAGINATED_FIELD_NUM_PAGE,
                PAGINATED_FIELD_HAS_NEXT,
                PAGINATED_FIELD_HAS_PREVIOUS,
            ],
            'properties': {
                PAGINATED_FIELD_DATA: schema,
                PAGINATED_FIELD_PAGE: {TYPE: TYPE_INT, EXAMPLE: 1},
                PAGINATED_FIELD_PER_PAGE: {TYPE: TYPE_INT, EXAMPLE: 20},
                PAGINATED_FIELD_TOTAL: {TYPE: TYPE_INT, EXAMPLE: 123},
                PAGINATED_FIELD_NUM_PAGE: {TYPE: TYPE_INT, EXAMPLE: 7},
                PAGINATED_FIELD_HAS_NEXT: {TYPE: TYPE_BOOL, EXAMPLE: True},
                PAGINATED_FIELD_HAS_PREVIOUS: {TYPE: TYPE_BOOL, EXAMPLE: False},
            },
        }
