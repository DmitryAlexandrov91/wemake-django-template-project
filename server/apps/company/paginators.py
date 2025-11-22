from typing import override

from rest_framework.request import Request

from server.apps.surveys.paginators import CustomPaginator


class DepartmentPaginator(CustomPaginator):
    """Paginator for DepartmentViewSet."""

    @override
    def get_page_size(self, request: Request) -> int | None:
        """Return page size from query params, or None if 'all' is specified."""
        raw = request.query_params.get(self.page_size_query_param)

        if raw == 'all':
            return None

        return super().get_page_size(request)
