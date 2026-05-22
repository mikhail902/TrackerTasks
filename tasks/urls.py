from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    ProjectViewSet, TaskViewSet,
    TaskCommentView, TaskHistoryView,
    NotificationView, NotificationReadView,
    TimeLogView
)

app_name = 'tasks'

router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('', TaskViewSet, basename='tasks')

urlpatterns = [
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('<int:task_id>/comments/', TaskCommentView.as_view(), name='task-comments'),
    path('<int:task_id>/history/', TaskHistoryView.as_view(), name='task-history'),
    path('<int:task_id>/timelogs/', TimeLogView.as_view(), name='task-timelogs'),
]

urlpatterns += router.urls