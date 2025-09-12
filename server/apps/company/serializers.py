from rest_framework import serializers

from server.apps.company.models import Department


class DepartmentCreateSerializer(serializers.ModelSerializer['Department']):
    """Serializer for creating a Department.

    Accepts and returns `department_name` (maps to `Department.name` in DB).
    """

    department_name = serializers.CharField(source='name')

    class Meta:
        model = Department
        fields = ('id', 'department_name')
