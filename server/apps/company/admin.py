from django.contrib import admin

from server.apps.company.models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin[Department]):
    """Admin interface for the Department model."""

    list_display = ('name', 'description', 'head', 'to_delete')  # noqa: WPS226
    search_fields = (
        'name',
        'head__username',
        'head__email',
    )
    list_filter = ('head', 'to_delete')
    fields = ('name', 'description', 'head', 'to_delete')

    list_select_related = ('head',)
