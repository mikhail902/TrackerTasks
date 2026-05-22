from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Project, Task, TaskComment, TaskHistory, Notification, TimeLog
from .serializer import (
    ProjectSerializer, ProjectCreateSerializer,
    TaskSerializer, TaskCreateSerializer,
    TaskCommentSerializer, TaskHistorySerializer,
    TaskStatusSerializer, TaskAssignSerializer,
    NotificationSerializer, TimeLogSerializer,
)
from .paginators import TaskPagination, NotificationPagination
from .permissions import IsAdminOrManager, IsAdmin, IsCreatorOrAssignee


class ProjectViewSet(ModelViewSet):
    """CRUD проектов"""
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


class TaskViewSet(ModelViewSet):
    """CRUD задач"""
    queryset = Task.objects.all()
    pagination_class = TaskPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        task = serializer.save(creator=self.request.user)
        TaskHistory.objects.create(
            task=task, user=self.request.user,
            field_name='status', new_value=task.status
        )
        if task.assignee:
            Notification.objects.create(
                user=task.assignee, type='task_assigned',
                message=f'Вам назначена задача: {task.title}', task=task
            )

    def perform_update(self, serializer):
        old_task = Task.objects.get(pk=self.kwargs.get('pk'))
        task = serializer.save()

        if old_task.status != task.status:
            TaskHistory.objects.create(
                task=task, user=self.request.user,
                field_name='status', old_value=old_task.status, new_value=task.status
            )
            if task.status == 'done':
                task.completed_at = timezone.now()
                task.save()

            Notification.objects.create(
                user=task.creator, type='task_status',
                message=f'Статус задачи "{task.title}" изменён на {task.get_status_display()}',
                task=task
            )

        if old_task.assignee != task.assignee and task.assignee:
            TaskHistory.objects.create(
                task=task, user=self.request.user,
                field_name='assignee',
                old_value=str(old_task.assignee),
                new_value=str(task.assignee)
            )
            Notification.objects.create(
                user=task.assignee, type='task_assigned',
                message=f'Вам назначена задача: {task.title}', task=task
            )

    @action(detail=False, methods=['get'], url_path='my')
    def my_tasks(self, request):
        """Мои созданные задачи"""
        tasks = self.get_queryset().filter(creator=request.user)
        page = self.paginate_queryset(tasks)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='assigned')
    def assigned_tasks(self, request):
        """Назначенные мне задачи"""
        tasks = self.get_queryset().filter(assignee=request.user)
        page = self.paginate_queryset(tasks)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        """Назначить исполнителя"""
        task = self.get_object()
        serializer = TaskAssignSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        """Изменить статус"""
        task = self.get_object()
        serializer = TaskStatusSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TaskCommentView(ListCreateAPIView):
    """Комментарии к задаче"""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskComment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs.get('task_id'))
        comment = serializer.save(author=self.request.user, task=task)

        if task.creator != self.request.user:
            Notification.objects.create(
                user=task.creator, type='task_comment',
                message=f'Новый комментарий к задаче "{task.title}"',
                task=task
            )
        if task.assignee and task.assignee != self.request.user:
            Notification.objects.create(
                user=task.assignee, type='task_comment',
                message=f'Новый комментарий к задаче "{task.title}"',
                task=task
            )


class TaskHistoryView(ListAPIView):
    """История изменений задачи"""
    serializer_class = TaskHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskHistory.objects.filter(task_id=task_id)


class NotificationView(ListAPIView):
    """Уведомления пользователя"""
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationReadView(APIView):
    """Отметить уведомление прочитанным"""
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})


class TimeLogView(ListCreateAPIView):
    """Учёт времени по задаче"""
    serializer_class = TimeLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TimeLog.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs.get('task_id'))
        timelog = serializer.save(user=self.request.user, task=task)
        task.spent_hours += timelog.hours
        task.save()