from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from server.apps.company.models import Department
from server.apps.users.models import CustomUser


class DepartmentCreateSerializer(serializers.ModelSerializer[Department]):
    """Serializer for creating a Department.

    Accepts and returns `department_name` (maps to `Department.name` in DB).
    """

    department_name = serializers.CharField(
        source='name',
        validators=[
            UniqueValidator(
                queryset=Department.objects.all().select_related(),
                message='This department name already exists',
            ),
        ],
    )

    class Meta:
        model = Department
        fields = ('id', 'department_name')


class UserSerializer(serializers.ModelSerializer[CustomUser]):
    """Serializer for CustomUser model with id and name fields."""

    class Meta:
        model = CustomUser
        fields = ('id', 'full_name')


class DepartmentSerializer(serializers.ModelSerializer[Department]):
    """Serializer for Department model with employees list and count."""

    department_name = serializers.CharField(source='name')
    employees = UserSerializer(source='users', many=True, read_only=True)
    employees_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ('id', 'department_name', 'employees_count', 'employees')
