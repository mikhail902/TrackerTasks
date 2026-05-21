from rest_framework import serializers
from django.utils import timezone


class TaskValidator:
    """Валидация задачи"""

    def __call__(self, data):
        deadline = data.get('deadline')
        status = data.get('status')
        parent_task = data.get('parent_task')

        if deadline and deadline < timezone.now() and not status:
            raise serializers.ValidationError({'deadline': 'Дедлайн не может быть в прошлом.'})

        if parent_task and hasattr(self, 'instance') and parent_task == self.instance:
            raise serializers.ValidationError({'parent_task': 'Задача не может быть подзадачей самой себя.'})