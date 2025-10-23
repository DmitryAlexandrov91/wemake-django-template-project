import os
from typing import Any

from celery import Celery
from celery.schedules import crontab

from server.apps.users.tasks import inactivate_marked_users_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')


app = Celery('server')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.on_after_finalize.connect  # type: ignore[misc]
def setup_periodic_tasks(sender: Celery, **kwargs: object) -> None:
    """Create the mid-night users inactivation task."""
    _create_periodic_task(
        sender, crontab(minute=0, hour=0), inactivate_marked_users_task
    )


def _create_periodic_task(sender: Celery, schedule: crontab, task: Any) -> None:
    """Adding periodic task to db."""
    sender.add_periodic_task(schedule, task.s(), name=task.__name__)
