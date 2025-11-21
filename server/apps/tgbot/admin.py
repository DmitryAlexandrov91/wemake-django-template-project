from django.contrib import admin

from server.apps.tgbot.models import TgUserState


@admin.register(TgUserState)
class TgUserStateAdmin(admin.ModelAdmin[TgUserState]):
    """Admin class for TgUserState."""

    list_display = (
        'id',
        'chat_id',
        'user_id',
        'state',
        'state_data',
    )
