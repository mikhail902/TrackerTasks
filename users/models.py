from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', email)
        return self.create_user(email, password, **extra_fields)


class Department(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название отдела')
    description = models.TextField(blank=True, verbose_name='Описание')
    manager = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_departments', verbose_name='Руководитель'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return self.name


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Руководитель'),
        ('employee', 'Сотрудник'),
    ]

    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='employee', verbose_name='Роль')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employees', verbose_name='Отдел'
    )
    position = models.CharField(max_length=100, blank=True, verbose_name='Должность')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Telegram Chat ID')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name} {self.middle_name or ""}'.strip()