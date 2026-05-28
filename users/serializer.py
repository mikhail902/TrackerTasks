from rest_framework.serializers import ModelSerializer, SerializerMethodField
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
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def get_full_name(self, obj):
        return obj.full_name

    def get_department_name(self, obj):
        if obj.department:
            return obj.department.name
        return None


class UserShortSerializer(ModelSerializer):
    full_name = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'position', 'avatar')

    def get_full_name(self, obj):
        return obj.full_name


class UserUpdateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'phone', 'position', 'telegram_chat_id')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'middle_name': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
            'position': {'required': False, 'allow_blank': True},
            'telegram_chat_id': {'required': False, 'allow_blank': True},
        }