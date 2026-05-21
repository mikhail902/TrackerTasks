from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Task, Notification
from .services import send_telegram_message


@shared_task
def check_deadlines():
    """Проверяет задачи с приближающимся дедлайном (24 часа)"""
    now = timezone.now()
    deadline_threshold = now + timedelta(hours=24)

    tasks = Task.objects.filter(
        deadline__lte=deadline_threshold,
        deadline__gt=now,
        status__in=['todo', 'in_progress']
    ).select_related('assignee', 'creator')

    for task in tasks:
        if task.assignee and task.assignee.telegram_chat_id:
            send_telegram_message(
                task.assignee.telegram_chat_id,
                f'⏰ Приближается дедлайн!\n'
                f'Задача: {task.title}\n'
                f'Дедлайн: {task.deadline.strftime("%d.%m.%Y %H:%M")}\n'
                f'Приоритет: {task.get_priority_display()}'
            )

        Notification.objects.create(
            user=task.assignee or task.creator,
            type='deadline_soon',
            message=f'Приближается дедлайн задачи: {task.title}',
            task=task
        )

    return f'Проверено {tasks.count()} задач'


@shared_task
def send_task_notification(task_id, user_id, notification_type, message):
    """Отправка уведомления о задаче"""
    notification = Notification.objects.create(
        user_id=user_id,
        type=notification_type,
        message=message,
        task_id=task_id
    )
    return notification.id