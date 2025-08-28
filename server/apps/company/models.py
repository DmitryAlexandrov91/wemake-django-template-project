from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Department(models.Model):
    """The department model in the company."""

    name = models.CharField()
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
