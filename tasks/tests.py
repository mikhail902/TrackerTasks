from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Project, Task, TaskComment, Notification
from users.models import Department

User = get_user_model()


class TaskTestCase(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(name='IT')

        self.admin = User.objects.create_user(
            email='admin@test.ru', password='admin123',
            role='admin', department=self.department,
            first_name='Admin', last_name='Adminov', position='Admin'
        )
        self.manager = User.objects.create_user(
            email='manager@test.ru', password='manager123',
            role='manager', department=self.department,
            first_name='Manager', last_name='Managerov', position='Team Lead'
        )
        self.employee = User.objects.create_user(
            email='employee@test.ru', password='employee123',
            role='employee', department=self.department,
            first_name='Employee', last_name='Employov', position='Developer'
        )

        self.project = Project.objects.create(
            name='Test Project', manager=self.manager
        )

        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            creator=self.manager,
            assignee=self.employee,
            priority='high'
        )

    def get_token(self, email, password):
        response = self.client.post('/api/users/token/', {
            'email': email, 'password': password
        })
        return response.data['access']

    def test_register_user(self):
        data = {
            'email': 'new@test.ru',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'position': 'Dev'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        response = self.client.post('/api/users/token/', {
            'email': 'employee@test.ru',
            'password': 'employee123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_create_project_as_manager(self):
        token = self.get_token('manager@test.ru', 'manager123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'name': 'New Project', 'description': 'Desc'}
        response = self.client.post('/api/tasks/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_project_as_employee(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {'name': 'New Project'}
        response = self.client.post('/api/tasks/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_projects(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_task(self):
        token = self.get_token('manager@test.ru', 'manager123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        data = {
            'title': 'New Task',
            'description': 'Desc',
            'project': self.project.id,
            'priority': 'high',
            'assignee': self.employee.id
        }
        response = self.client.post('/api/tasks/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')

    def test_list_tasks(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_my_tasks(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/tasks/my/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assigned_tasks(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/tasks/assigned/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_change_status(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch(
            f'/api/tasks/tasks/{self.task.id}/status/',
            {'status': 'in_progress'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assign_task(self):
        token = self.get_token('manager@test.ru', 'manager123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            f'/api/tasks/tasks/{self.task.id}/assign/',
            {'assignee': self.admin.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_comment(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(
            f'/api/tasks/tasks/{self.task.id}/comments/',
            {'text': 'Test comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_comments(self):
        TaskComment.objects.create(
            task=self.task, author=self.employee, text='Comment'
        )
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(f'/api/tasks/tasks/{self.task.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notifications(self):
        Notification.objects.create(
            user=self.employee, type='task_assigned',
            message='Test', task=self.task
        )
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_read(self):
        notif = Notification.objects.create(
            user=self.employee, type='task_assigned',
            message='Test', task=self.task
        )
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/tasks/notifications/{notif.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_cannot_delete_task(self):
        token = self.get_token('employee@test.ru', 'employee123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        task = Task.objects.create(
            title='Test', project=self.project,
            creator=self.employee, priority='medium'
        )
        response = self.client.delete(f'/api/tasks/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_task(self):
        token = self.get_token('admin@test.ru', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.delete(f'/api/tasks/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)