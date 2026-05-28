from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from users.models import User
from .models import Project, ProjectInvitation, Task, TaskComment, TaskHistory, Notification, TimeLog
from .serializer import (
    ProjectSerializer, ProjectCreateSerializer,
    TaskSerializer, TaskCreateSerializer,
    TaskCommentSerializer, TaskHistorySerializer,
    TaskStatusSerializer, TaskAssignSerializer,
    NotificationSerializer, TimeLogSerializer,
)
from .paginators import TaskPagination, NotificationPagination
from .permissions import IsAdminOrManager, IsCreatorOrAssignee

class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Project.objects.all()
        return Project.objects.filter(
            Q(manager=user) | Q(team=user)
        ).distinct()


class ProjectInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, manager=request.user)
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обязателен'}, status=400)
        try:
            invited_user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        invitation, created = ProjectInvitation.objects.get_or_create(
            project=project, email=email, user=invited_user,
            defaults={'sender': request.user}
        )
        if not created:
            return Response({'error': 'Приглашение уже отправлено'}, status=400)

        Notification.objects.create(
            user=invited_user, type='mention',
            message=f'{request.user.full_name} приглашает вас в проект "{project.name}"',
        )
        return Response({'status': 'invited'})

    def patch(self, request, project_id):
        """Принять или отклонить приглашение"""
        action = request.data.get('action')
        invitation = get_object_or_404(
            ProjectInvitation, project_id=project_id, user=request.user, status='pending'
        )
        if action == 'accept':
            invitation.status = 'accepted'
            invitation.save()
            invitation.project.team.add(request.user)
            return Response({'status': 'accepted'})
        elif action == 'decline':
            invitation.status = 'declined'
            invitation.save()
            return Response({'status': 'declined'})
        return Response({'error': 'Неверное действие'}, status=400)


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    pagination_class = TaskPagination
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='project-users')
    def project_users(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response([])
        project = get_object_or_404(Project, pk=project_id)
        users = [project.manager] + list(project.team.all())
        data = [{'id': u.id, 'full_name': u.full_name} for u in users if u]
        return Response(data)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateSerializer
        return TaskSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsCreatorOrAssignee()]
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

    def get_queryset(self):
        user = self.request.user
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()

        qs = Task.objects.all()
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)

        if user.role == 'admin':
            return qs

        return qs.filter(
            Q(creator=user) | Q(assignee=user) | Q(project__team=user) | Q(project__manager=user)
        ).distinct()

    @action(detail=False, methods=['get'], url_path='my')
    def my_tasks(self, request):
        tasks = self.get_queryset().filter(creator=request.user)
        page = self.paginate_queryset(tasks)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], url_path='assigned')
    def assigned_tasks(self, request):
        tasks = self.get_queryset().filter(assignee=request.user)
        page = self.paginate_queryset(tasks)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        task = self.get_object()
        serializer = TaskAssignSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        task = self.get_object()
        serializer = TaskStatusSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='share')
    def share_task(self, request, pk=None):
        task = self.get_object()
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        task.shared_with.add(user)
        Notification.objects.create(
            user=user, type='mention',
            message=f'{request.user.full_name} поделился задачей "{task.title}"',
            task=task
        )
        return Response({'status': 'shared'})


class TaskCommentView(ListCreateAPIView):
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
                message=f'Новый комментарий к задаче "{task.title}"', task=task
            )
        if task.assignee and task.assignee != self.request.user:
            Notification.objects.create(
                user=task.assignee, type='task_comment',
                message=f'Новый комментарий к задаче "{task.title}"', task=task
            )


class TaskHistoryView(ListAPIView):
    serializer_class = TaskHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskHistory.objects.filter(task_id=task_id)


class NotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})


class TimeLogView(ListCreateAPIView):
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


class BusyEmployeesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employees = User.objects.filter(is_active=True).annotate(
            active_tasks=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['todo', 'in_progress', 'review']))
        ).order_by('-active_tasks')

        data = [{
            'id': e.id,
            'full_name': e.full_name,
            'position': e.position,
            'department': e.department.name if e.department else None,
            'active_tasks': e.active_tasks,
        } for e in employees]
        return Response(data)


class ImportantTasksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        important = Task.objects.filter(
            status__in=['todo', 'backlog', 'cancelled'],
            subtasks__status__in=['in_progress', 'review']
        ).distinct()

        least_busy = User.objects.filter(is_active=True).annotate(
            task_count=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['todo', 'in_progress', 'review']))
        ).order_by('task_count').first()

        result = []
        for task in important:
            candidates = []
            if least_busy:
                candidates.append(least_busy)
            if task.parent_task and task.parent_task.assignee:
                parent_assignee = task.parent_task.assignee
                parent_count = parent_assignee.assigned_tasks.filter(
                    status__in=['todo', 'in_progress', 'review']
                ).count()
                least_count = least_busy.assigned_tasks.filter(
                    status__in=['todo', 'in_progress', 'review']
                ).count() if least_busy else 0
                if parent_count <= least_count + 2:
                    if parent_assignee not in candidates:
                        candidates.append(parent_assignee)

            result.append({
                'id': task.id,
                'title': task.title,
                'deadline': task.deadline,
                'status': task.status,
                'priority': task.priority,
                'project': task.project_name,
                'candidates': [{'id': c.id, 'full_name': c.full_name} for c in candidates],
            })
        return Response(result)

class NotificationHandleInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        action = request.data.get('action')

        invitation = ProjectInvitation.objects.filter(
            user=request.user, status='pending'
        ).first()

        if not invitation:
            return Response({'error': 'Приглашение не найдено'}, status=404)

        if action == 'accept':
            invitation.status = 'accepted'
            invitation.save()
            invitation.project.team.add(request.user)
            return Response({'status': 'accepted'})
        elif action == 'decline':
            invitation.status = 'declined'
            invitation.save()
            return Response({'status': 'declined'})

        return Response({'error': 'Неверное действие'}, status=400)


class ProjectRemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, manager=request.user)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id обязателен'}, status=400)
        user = get_object_or_404(User, pk=user_id)
        project.team.remove(user)
        return Response({'status': 'removed'})