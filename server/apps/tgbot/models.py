from typing import final

from django.db import models

from server.common.constants import DATA_LENGTH


@final
class TgUserState(models.Model):
    """Storage for Telegram bot user states with full state management."""

    chat_id = models.BigIntegerField(
        default=0,
    )
    user_id = models.BigIntegerField()
    state = models.CharField(
        max_length=DATA_LENGTH,
        blank=True,
        default='',
    )
    state_data = models.JSONField(
        default=dict,
        blank=True,
    )
