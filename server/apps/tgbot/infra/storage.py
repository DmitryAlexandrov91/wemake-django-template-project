from typing import Any, override

from django.db import transaction
from telebot.storage import StateDataContext, StateStorageBase

from server.apps.tgbot.models import TgUserState


class StatePostgresStorage(StateStorageBase):  # noqa: WPS214
    """PostgreSQL-based state storage for pyTelegramBotAPI."""

    @override
    def set_state(  # noqa: WPS211, WPS615
        self,
        chat_id: int,
        user_id: int,
        state: str,
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> bool:
        """Set state for user."""
        with transaction.atomic():
            state_obj = self._get_or_create_state(chat_id, user_id)
            state_obj.state = state
            state_obj.save()

        return True

    @override
    def get_state(  # noqa: WPS615
        self,
        chat_id: int,
        user_id: int,
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> str | None:
        """Get state for user."""
        try:
            state_obj = TgUserState.objects.get(
                chat_id=chat_id, user_id=user_id
            )
        except TgUserState.DoesNotExist:
            return None
        return state_obj.state or None

    @override
    def delete_state(
        self,
        chat_id: int,
        user_id: int,
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> None:
        """Delete state for user."""
        TgUserState.objects.filter(chat_id=chat_id, user_id=user_id).delete()

    @override
    def reset_data(
        self,
        chat_id: int,
        user_id: int,
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> None:
        """Reset data for user."""
        TgUserState.objects.filter(
            chat_id=chat_id,
            user_id=user_id,
        ).update(state_data={})

    @override
    def get_interactive_data(
        self,
        chat_id: int,
        user_id: int,
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> StateDataContext:
        """Get interactive data for user."""
        return StateDataContext(  # type: ignore[no-untyped-call]
            self,
            chat_id=chat_id,
            user_id=user_id,
            business_connection_id=business_connection_id,
            message_thread_id=message_thread_id,
            bot_id=bot_id,
        )

    @override
    def get_data(  # noqa: WPS615
        self,
        chat_id: int,
        user_id: int,
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> dict[str, Any]:
        """Get all data for user."""
        try:
            state_obj = TgUserState.objects.get(
                chat_id=chat_id,
                user_id=user_id,
            )
        except TgUserState.DoesNotExist:
            return {}
        return state_obj.state_data or {}

    @override
    def set_data(  # noqa: WPS211, WPS615
        self,
        chat_id: int,
        user_id: int,
        key: str,
        value: Any,  # noqa: WPS110
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> Any:
        """Set data for user."""
        with transaction.atomic():
            state_obj = self._get_or_create_state(chat_id, user_id)
            state_obj.state_data[key] = value
            state_obj.save()

    @override
    def save(  # noqa: WPS211
        self,
        chat_id: int,
        user_id: int,
        data: dict[str, Any],  # noqa: WPS110
        business_connection_id: Any = None,
        message_thread_id: Any = None,
        bot_id: Any = None,
    ) -> Any:
        """Save data for user."""
        with transaction.atomic():
            state_obj = self._get_or_create_state(chat_id, user_id)
            state_obj.state_data = data
            state_obj.save()

    def _get_or_create_state(
        self,
        chat_id: int,
        user_id: int,
    ) -> TgUserState:
        """Get or create user state record."""
        state_obj, _ = TgUserState.objects.get_or_create(
            chat_id=chat_id,
            user_id=user_id,
            defaults={'state_data': {}},
        )
        return state_obj
