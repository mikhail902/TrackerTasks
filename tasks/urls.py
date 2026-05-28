from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import (
    ProjectViewSet, ProjectInvitationView, TaskViewSet,
    TaskCommentView, TaskHistoryView,
    NotificationView, NotificationReadView,
    TimeLogView, BusyEmployeesView, ImportantTasksView, NotificationHandleInviteView, ProjectRemoveMemberView
)

app_name = 'tasks'

router = SimpleRouter()
router.register('projects', ProjectViewSet, basename='projects')
router.register('tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('projects/<int:project_id>/remove-member/', ProjectRemoveMemberView.as_view(), name='project-remove-member'),
    path('notifications/<int:notification_id>/handle-invite/', NotificationHandleInviteView.as_view(), name='notification-handle-invite'),
    path('projects/<int:project_id>/invite/', ProjectInvitationView.as_view(), name='project-invite'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('tasks/<int:task_id>/comments/', TaskCommentView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/history/', TaskHistoryView.as_view(), name='task-history'),
    path('tasks/<int:task_id>/timelogs/', TimeLogView.as_view(), name='task-timelogs'),
    path('busy-employees/', BusyEmployeesView.as_view(), name='busy-employees'),
    path('important-tasks/', ImportantTasksView.as_view(), name='important-tasks'),
]

urlpatterns += router.urls