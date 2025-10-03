from typing import Any, ClassVar, override

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinLengthValidator
from django.db import models

from server.apps.users.validators import validate_telegram_username

EMAIL_MAX_LENGTH = 256
FULL_NAME_MAX_LENGTH = 256
POSITION_MAX_LENGTH = 128
ROLE_MAX_LENGTH = 128
TELEGRAM_USERNAME_MAX_LENGTH = 33
TELEGRAM_USERNAME_MIN_LENGTH = 6

REGISTRATION_EMAIL_REQUIRED_ERROR = 'Email is required!'


class _CustomUserManager(BaseUserManager['CustomUser']):
    """
    Custom manager for the CustomUser model.

    This manager handles user creation using email as the primary identifier.
    It provides methods to create regular users and superusers.
    """

    def create_user(
        self, email: str, password: str | None, **extra_fields: Any
    ) -> 'CustomUser':
        """
        Create and save a regular user with the given email and password.

        Args:
            email (str): The email address of the user. Must be unique.
            password (str, optional): The user's password. Defaults to None.
            **extra_fields: Additional fields to set on the user instance.

        Raises:
            ValueError: If the email is not provided.

        Returns:
            CustomUser: The created user instance.
        """
        if not email:
            raise ValueError(REGISTRATION_EMAIL_REQUIRED_ERROR)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None, **extra_fields: Any
    ) -> 'CustomUser':
        """
        Create and save a superuser with the given email and password.

        Args:
            email (str): The email address of the superuser.
            password (str, optional): The superuser's password.
            **extra_fields: Additional fields to set on the superuser instance.

        Raises:
            ValueError: If 'is_staff' or 'is_superuser' are not True.

        Returns:
            CustomUser: The created superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that replaces Django's default User.

    This model uses email as the primary username and adds custom fields
    such as patronymic, position, and role. It can also be linked to
    other models like departments.

    Attributes:
        email (EmailField): Unique email used as the username.
        full_name (CharField): User's full name.
        position (CharField): User's position in the organization (optional).
        role (CharField): User's role (optional).
        is_active (BooleanField): Indicates whether the user account is active.
        is_staff (BooleanField): Determines if the user can access admin site.
        tg_id (PositiveBigIntegerField): Unique telegram id.
        edited_at (DateTimeField) - the time of last edit.
    """

    email = models.EmailField(
        'Email',
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        help_text='Enter your email: ',
    )
    full_name = models.CharField(
        'Full name',
        max_length=FULL_NAME_MAX_LENGTH,
        help_text='Enter your full name: ',
        default='Unknown',
    )
    position = models.CharField(
        'Position',
        max_length=POSITION_MAX_LENGTH,
        blank=True,
        help_text='Enter your possition: ',
    )
    role = models.CharField(
        'Role',
        max_length=ROLE_MAX_LENGTH,
        blank=True,
        help_text='Enter your role: ',
    )
    department = models.ForeignKey(
        'company.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Select the user's department (optional): ",
    )
    is_active = models.BooleanField(
        'Active status',
        default=True,
    )
    is_staff = models.BooleanField(
        'Staff status',
        default=True,
    )
    tg_username = models.CharField(
        'Telegram username',
        blank=True,
        max_length=TELEGRAM_USERNAME_MAX_LENGTH,
        help_text='Enter your telegram @username: ',
        validators=(
            validate_telegram_username,
            MinLengthValidator(TELEGRAM_USERNAME_MIN_LENGTH),
        ),
    )
    edited_at = models.DateTimeField(
        'Время редактирования', auto_now=True, null=True
    )

    objects = _CustomUserManager()  # noqa: WPS110

    USERNAME_FIELD = 'email'  # noqa: WPS115
    EMAIL_FIELD = 'email'  # noqa: WPS115
    REQUIRED_FIELDS: ClassVar[list[str]] = ['full_name']  # noqa: WPS115

    class Meta:
        """
        Metadata for the CustomUser model.

        Ordering is by email, full name.
        Default related name for reverse relations is 'users'.
        """

        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = (
            'email',
            'full_name',
        )
        default_related_name = 'users'
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=('tg_username',),
                name='unique_tg_username_not_blank',
                condition=~models.Q(tg_username=''),
            )
        ]

    @override
    def __str__(self) -> str:
        """Return the string representation of the user."""
        return self.email
