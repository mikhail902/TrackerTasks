from django.contrib import admin
from .models import Project, Task, TaskComment, Notification, TimeLog, Tag

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'status', 'deadline', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'assignee', 'deadline', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title',)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'is_read', 'created_at')

@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'hours', 'date')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'project')