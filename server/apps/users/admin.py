from typing import Any, Final, override

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest

from server.apps.surveys.models import UserStatistics
from server.apps.users.models import CustomUser

_EMAIL_FIELD: Final = 'email'
_FULL_NAME_FIELD: Final = 'full_name'
_FIELDS: Final = 'fields'


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin[CustomUser]):  # type: ignore[type-var]
    """This class represents user in admin panel."""

    list_display = (
        _EMAIL_FIELD,
        _FULL_NAME_FIELD,
        'is_staff',
        'is_active',
        'average_answer_sec',
    )
    list_filter = (
        'is_staff',
        'is_active',
        'groups',
        'department',
    )
    search_fields = (_EMAIL_FIELD, _FULL_NAME_FIELD)
    ordering = (_EMAIL_FIELD,)
    filter_horizontal = ('groups', 'user_permissions')
    list_select_related = ('department', 'statistics')

    fieldsets = (
        (None, {_FIELDS: (_EMAIL_FIELD, 'password')}),
        (
            'Personal info',
            {
                _FIELDS: (
                    _FULL_NAME_FIELD,
                    'position',
                    'role',
                    'department',
                    'tg_username',
                )
            },
        ),
        (
            'Permissions',
            {
                _FIELDS: (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        ('Important dates', {_FIELDS: ('last_login', 'edited_at')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                _FIELDS: ('email', 'full_name', 'password1', 'password2'),
            },
        ),
    )

    readonly_fields = ('edited_at',)

    def average_answer_sec(self, user: CustomUser) -> Any:
        """Returns related statistics data."""
        try:
            return user.statistics.average_answer_sec
        except Exception:
            return 0


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin[UserStatistics]):
    """Fake registration of user statistics model."""

    @override
    def has_add_permission(self, request: HttpRequest) -> bool:
        """Adding new objects prohibited."""
        return False

    @override
    def has_change_permission(
        self, request: HttpRequest, object: Any | None = None
    ) -> bool:
        """Changing objects prohibited."""
        return False

    @override
    def has_delete_permission(
        self, request: HttpRequest, object: Any | None = None
    ) -> bool:
        """Object deletion prohibited."""
        return False
