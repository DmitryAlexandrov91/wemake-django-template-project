from typing import override

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Django AppConfig for the `users` app."""

    default_auto_field = 'django.db.models.AutoField'
    name = 'server.apps.users'

    @override
    def ready(self) -> None:
        """Import DRF Spectacular schema extensions on app ready."""
        import server.apps.users.drf_spectacular_schemas  # noqa
