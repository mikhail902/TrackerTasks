from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from .models import User, Department


class DepartmentSerializer(ModelSerializer):
    manager_name = SerializerMethodField()
    employees_count = SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_manager_name(self, obj):
        if obj.manager:
            return obj.manager.full_name
        return None

    def get_employees_count(self, obj):
        return obj.employees.count()


class UserSerializer(ModelSerializer):
    full_name = SerializerMethodField()
    department_name = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'password', 'first_name', 'last_name',
            'middle_name', 'full_name', 'role', 'department',
            'department_name', 'position', 'phone', 'avatar',
            'telegram_chat_id', 'is_active', 'created_at'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True},
        }

    def get_full_name(self, obj):
        return obj.full_name

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None


class UserShortSerializer(ModelSerializer):
    """Краткая информация о пользователе для списков"""
    full_name = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'position', 'avatar')

    def get_full_name(self, obj):
        return obj.full_name


class UserUpdateSerializer(ModelSerializer):
    """Обновление профиля без пароля"""

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'middle_name',
            'phone', 'avatar', 'telegram_chat_id', 'position'
        )