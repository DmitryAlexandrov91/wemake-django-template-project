from typing import Any, override

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
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')
