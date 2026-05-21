from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic import TemplateView

schema_view = get_schema_view(
    openapi.Info(
        title='Task Tracker API',
        default_version='v1',
        description='API для трекера задач сотрудников',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='admin@example.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),

    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls', namespace='users')),
    path('api/tasks/', include('tasks.urls', namespace='tasks')),
    path('', TemplateView.as_view(template_name='login.html')),
    path('login/', TemplateView.as_view(template_name='login.html')),
    path('register/', TemplateView.as_view(template_name='register.html')),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html')),
    path('projects/', TemplateView.as_view(template_name='projects.html')),
    path('tasks/', TemplateView.as_view(template_name='tasks.html')),
    path('tasks/<int:id>/', TemplateView.as_view(template_name='task_detail.html')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)