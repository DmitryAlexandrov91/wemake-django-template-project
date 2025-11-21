from typing import override

from django.contrib.auth import get_user_model
from django.db import models

from server.common.constants import DATA_LENGTH

User = get_user_model()


class Department(models.Model):
    """The department model in the company."""

    name = models.CharField(max_length=DATA_LENGTH, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='company_departments',
    )
    to_delete = models.BooleanField(default=0)

    @override
    def __str__(self) -> str:
        """
        Str method for department.

        >>> department = Department(name='Department1')
        >>> str(department)
        'Department1'
        """
        return self.name
