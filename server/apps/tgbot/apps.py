from typing import override

from django.apps import AppConfig


class TgbotConfig(AppConfig):
    """Configuration for the tgbot Django application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server.apps.tgbot'

    @override
    def ready(self) -> None:
        from server.apps.tgbot import entrypoints  # noqa: PLC0415,F401
