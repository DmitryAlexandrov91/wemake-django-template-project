from dataclasses import dataclass

from server.apps.tgbot.services import TelegramService


@dataclass
class ProcessTelegramUpdate:
    """Usecase for process update bot."""

    _telegram_service: TelegramService

    def __call__(self, request_body: bytes) -> None:
        """Use service for bot update."""
        self._telegram_service.process_update(request_body)
