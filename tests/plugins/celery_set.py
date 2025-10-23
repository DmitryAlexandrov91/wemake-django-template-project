import pytest
from django.conf import LazySettings


@pytest.fixture(autouse=True)
def setup_celery_eager(settings: LazySettings) -> None:
    """Tuning Celery."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_RESULT_BACKEND = 'cache'
