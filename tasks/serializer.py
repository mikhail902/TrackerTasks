from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from django.utils import timezone
from .models import Project, Tag, Task, TaskComment, TaskHistory, Notification, TimeLog
from users.serializer import UserShortSerializer


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ProjectSerializer(ModelSerializer):
    manager = UserShortSerializer(read_only=True)
    team = UserShortSerializer(many=True, read_only=True)
    tasks_count = SerializerMethodField()
    completed_tasks_count = SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_tasks_count(self, obj):
        return obj.tasks.count()

    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(status='done').count()


class ProjectCreateSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ('name', 'description', 'deadline', 'team')
        extra_kwargs = {'team': {'required': False}}


class TaskCommentSerializer(ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ('author', 'task', 'created_at', 'updated_at')


class TaskHistorySerializer(ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = TaskHistory
        fields = '__all__'


class TimeLogSerializer(ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = TimeLog
        fields = '__all__'
        read_only_fields = ('user', 'created_at')


class TaskSerializer(ModelSerializer):
    creator = UserShortSerializer(read_only=True)
    assignee = UserShortSerializer(read_only=True)
    reviewer = UserShortSerializer(read_only=True)
    project_name = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    subtasks_count = SerializerMethodField()
    comments_count = SerializerMethodField()
    is_overdue = SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('creator', 'created_at', 'updated_at', 'completed_at', 'spent_hours')

    def get_project_name(self, obj):
        if obj.project:
            return obj.project.name
        return None

    def get_subtasks_count(self, obj):
        return obj.subtasks.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_overdue(self, obj):
        if obj.deadline and obj.status not in ['done', 'cancelled']:
            return timezone.now() > obj.deadline
        return False


class TaskCreateSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'title', 'description', 'project', 'priority',
            'assignee', 'reviewer', 'deadline', 'estimated_hours',
            'parent_task', 'tags'
        )
        extra_kwargs = {
            'assignee': {'required': False},
            'reviewer': {'required': False},
            'deadline': {'required': False},
            'estimated_hours': {'required': False},
            'parent_task': {'required': False},
            'tags': {'required': False},
        }


class TaskStatusSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)


class TaskAssignSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('assignee',)


class NotificationSerializer(ModelSerializer):
    task_title = SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'task_title')

    def get_task_title(self, obj):
        if obj.task:
            return obj.task.title
        return None