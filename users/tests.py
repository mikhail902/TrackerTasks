from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Department

User = get_user_model()


class UserTestCase(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(name='HR')
        self.user = User.objects.create_user(
            email='test@test.ru',
            password='testpass123',
            first_name='Test',
            last_name='User',
            position='Dev',
            department=self.department
        )

    def get_token(self):
        response = self.client.post('/api/users/token/', {
            'email': 'test@test.ru',
            'password': 'testpass123'
        })
        return response.data['access']

    def test_register(self):
        data = {
            'email': 'new@test.ru',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'position': 'QA'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_duplicate_email(self):
        data = {
            'email': 'test@test.ru',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'position': 'Dev'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        response = self.client.post('/api/users/token/', {
            'email': 'test@test.ru',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile(self):
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile(self):
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.patch('/api/users/me/', {'first_name': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')