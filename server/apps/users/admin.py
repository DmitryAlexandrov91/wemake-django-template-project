from django.contrib import admin

from server.apps.users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin[CustomUser]):
    """Admin-class for CustomUser."""

    list_display = (
        'email',
        'full_name',
        'is_staff',
        'is_active',
    )
    list_filter = (
        'is_staff',
        'is_active',
        'groups',
    )
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')
    list_select_related = ('department',)
