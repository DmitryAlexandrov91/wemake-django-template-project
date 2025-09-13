from typing import Any, ClassVar, override

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)

from server.apps.users.models import CustomUser
from server.apps.users.services import AuthService
from server.di import resolve

User = get_user_model()

EMAIL_ATTR = 'email'


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for obtaining JWT tokens and only returns user-related data.

    Intended for scenarios where JWTs are stored in HttpOnly cookies
    instead of being returned in the response.
    """

    username_field = EMAIL_ATTR

    @override
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Validate the user credentials and return user data instead of JWTs.

        Steps:
        1. Call the parent class `validate` to check credentials and generate
           tokens.
        2. Remove 'access' and 'refresh' tokens from the response data.
        3. Add custom user information (id and email).

        Args:
            attrs (dict): The input data containing 'email' and 'password'.

        Returns:
            dict: User information without the JWT tokens.
        """
        response_data: dict[str, Any] = super().validate(attrs)
        return resolve(AuthService).remove_tokens_from_response(
            self, response_data
        )


class UserShortSerializer(serializers.ModelSerializer[CustomUser]):
    """CustomUser`s serializer."""

    id = serializers.IntegerField(source='pk', read_only=True)
    email = serializers.EmailField()
    full_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'full_name')


class EmployeeSerializer(serializers.ModelSerializer[Any]):
    """Сериализатор для работников."""

    department_name = serializers.CharField(
        source='department.name', read_only=True
    )
    telegram_id = serializers.IntegerField(
        source='tg_id', required=False, allow_null=True
    )
    survey_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields: ClassVar[list[str]] = [
            'id',
            'full_name',
            'department_name',
            'email',
            'telegram_id',
            'survey_count',
            'edited_at',
        ]
