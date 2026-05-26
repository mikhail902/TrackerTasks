from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    ProjectViewSet, TaskViewSet,
    TaskCommentView, TaskHistoryView,
    NotificationView, NotificationReadView,
    TimeLogView, BusyEmployeesView, ImportantTasksView
)

app_name = 'tasks'

router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('tasks/<int:task_id>/comments/', TaskCommentView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/history/', TaskHistoryView.as_view(), name='task-history'),
    path('tasks/<int:task_id>/timelogs/', TimeLogView.as_view(), name='task-timelogs'),
    path('busy-employees/', BusyEmployeesView.as_view(), name='busy-employees'),
    path('important-tasks/', ImportantTasksView.as_view(), name='important-tasks'),
]

urlpatterns += router.urls