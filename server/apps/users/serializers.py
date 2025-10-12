from typing import Any, ClassVar, override

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from server.apps.company.models import Department
from server.apps.users.infra.repository import UserRepoSave
from server.apps.users.models import CustomUser
from server.apps.users.services import AuthService
from server.di import resolve

User = get_user_model()

EMAIL_ATTR = 'email'
FULL_NAME_ATTR = 'full_name'
TG_ID_ATTR = 'tg_username'


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
        fields = (
            'id',
            EMAIL_ATTR,
            FULL_NAME_ATTR,
        )


class EmployeeReadSerializer(serializers.ModelSerializer[CustomUser]):
    """Serializer for read employees."""

    department_name = serializers.CharField(
        source='department.name', read_only=True
    )
    survey_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields: ClassVar[list[str]] = [
            'id',
            FULL_NAME_ATTR,
            'department_name',
            EMAIL_ATTR,
            TG_ID_ATTR,
            'survey_count',
            'edited_at',
        ]


class EmployeeCreateSerializer(serializers.ModelSerializer[CustomUser]):
    """Serializer for creating an empoyee."""

    full_name = serializers.CharField()
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message='This email already exists',
            ),
        ],
    )
    department_name = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Department.objects.all(),
    )

    class Meta:
        model = CustomUser
        fields = (
            FULL_NAME_ATTR,
            EMAIL_ATTR,
            'department_name',
            TG_ID_ATTR,
        )

    @override
    def create(self, validated_data: dict[str, Any]) -> CustomUser:
        """Employee creation."""
        validated_data['role'] = 'employee'
        validated_data['is_staff'] = False
        return resolve(UserRepoSave).create_user(**validated_data)

    @override
    def to_representation(self, employee: CustomUser) -> dict[str, Any]:
        """Employee serializer is applyed to return the new employee."""
        return EmployeeReadSerializer(employee).to_representation(employee)


class EmployeeUpdateSerializer(serializers.ModelSerializer[CustomUser]):
    """Serializer for updating an employee."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(),
                message='This email already exists',
            ),
        ],
    )
    full_name = serializers.CharField(required=False)
    department_name = serializers.SlugRelatedField(
        slug_field='name', queryset=Department.objects.all(), required=False
    )

    class Meta:
        model = CustomUser
        fields: ClassVar[list[str]] = [
            FULL_NAME_ATTR,
            EMAIL_ATTR,
            'department_name',
            TG_ID_ATTR,
        ]

    @override
    def update(
        self, instance: CustomUser, validated_data: dict[str, Any]
    ) -> CustomUser:
        """Employee update."""
        return resolve(UserRepoSave).update_user(instance, **validated_data)

    @override
    def to_representation(self, instance: CustomUser) -> dict[str, Any]:
        """Convert to response format."""
        return EmployeeReadSerializer(instance).data
