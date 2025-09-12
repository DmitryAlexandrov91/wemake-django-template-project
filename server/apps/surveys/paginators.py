from typing import override

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPaginator(PageNumberPagination):
    """Custom paginator."""

    page_size_query_param = 'per_page'

    @override
    def get_paginated_response(
        self, paginated_data: list[dict[str, int]]
    ) -> Response:
        """Return custom paginators`s response body."""
        page = getattr(self, 'page', None)
        if page is None:
            return Response({'data': paginated_data})
        return Response({
            'data': paginated_data,
            'page': page.number,
            'per_page': page.paginator.per_page,
            'total': page.paginator.count,
            'num_pages': page.paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
        })
