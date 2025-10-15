from server.apps.surveys.paginators import CustomPaginator
from server.apps.surveys.serializers_list import QuestionListSerializer


def test_get_paginated_response_schema() -> None:
    """Check that get_paginated_response_schema returns a dict."""
    paginator = CustomPaginator()
    schema = paginator.get_paginated_response_schema(QuestionListSerializer())
    assert isinstance(schema, dict)
