from rest_framework import serializers

from server.apps.company.models import Department


class DepartmentCreateSerializer(serializers.ModelSerializer['Department']):
    """Serializer for creating a Department."""

    department_name = serializers.CharField(source='name')

    class Meta:
        model = Department
        fields = ('id', 'department_name')
