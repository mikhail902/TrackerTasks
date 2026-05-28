from django.db import models
from django.conf import settings


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
        ('archived', 'Архив'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='managed_projects', verbose_name='Менеджер'
    )
    team = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        related_name='projects', verbose_name='Команда'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Дедлайн')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProjectInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    email = models.EmailField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_invitations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет (HEX)')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tags',
        null=True, blank=True, verbose_name='Проект'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        unique_together = ['name', 'project']

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критичный'),
    ]
    STATUS_CHOICES = [
        ('backlog', 'Бэклог'),
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('review', 'На проверке'),
        ('done', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]

    title = models.CharField(max_length=300, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks',
        null=True, blank=True, verbose_name='Проект'
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo', verbose_name='Статус')
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_tasks', verbose_name='Создатель'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tasks', verbose_name='Исполнитель'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='review_tasks', verbose_name='Проверяющий'
    )
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Дедлайн')
    estimated_hours = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        verbose_name='Оценка (часы)'
    )
    spent_hours = models.DecimalField(
        max_digits=5, decimal_places=1, default=0,
        verbose_name='Затрачено (часы)'
    )
    parent_task = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subtasks', verbose_name='Родительская задача'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks', verbose_name='Теги')
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        related_name='shared_tasks', verbose_name='Поделиться с'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.title


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name='Задача')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий #{self.id} к #{self.task_id}'


class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history', verbose_name='Задача')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    field_name = models.CharField(max_length=50, verbose_name='Поле')
    old_value = models.TextField(blank=True, null=True, verbose_name='Старое значение')
    new_value = models.TextField(blank=True, null=True, verbose_name='Новое значение')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'История изменений'
        verbose_name_plural = 'История изменений'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.field_name}: {self.old_value} → {self.new_value}'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('task_assigned', 'Назначена задача'),
        ('task_status', 'Изменён статус'),
        ('task_comment', 'Новый комментарий'),
        ('deadline_soon', 'Приближается дедлайн'),
        ('mention', 'Упоминание'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications', verbose_name='Пользователь'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип')
    message = models.TextField(verbose_name='Сообщение')
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='Задача'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_type_display()}: {self.message[:50]}'


class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='timelogs', verbose_name='Задача')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Сотрудник'
    )
    hours = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='Часы')
    description = models.TextField(blank=True, verbose_name='Описание работы')
    date = models.DateField(verbose_name='Дата')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Учёт времени'
        verbose_name_plural = 'Учёт времени'
        ordering = ['-date']

    def __str__(self):
        return f'{self.user}: {self.hours}ч'