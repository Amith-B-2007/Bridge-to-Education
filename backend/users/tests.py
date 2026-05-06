from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Student, Teacher
import json


class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_student_registration(self):
        data = {
            'user': {
                'username': 'testStudent',
                'email': 'student@test.com',
                'first_name': 'Test',
                'last_name': 'Student',
                'password': 'SecurePass123!'
            },
            'grade': 5,
            'school_name': 'Test School'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('user_id', response.data)

        self.assertTrue(User.objects.filter(username='testStudent').exists())
        user = User.objects.get(username='testStudent')
        self.assertTrue(Student.objects.filter(user=user).exists())

    def test_teacher_registration(self):
        data = {
            'user': {
                'username': 'testTeacher',
                'email': 'teacher@test.com',
                'first_name': 'Teacher',
                'last_name': 'Test',
                'password': 'SecurePass123!'
            },
            'school_name': 'Test School',
            'bio': 'Test teacher bio'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Teacher.objects.filter(user__username='testTeacher').exists())

    def test_registration_missing_fields(self):
        data = {'user': {'username': 'incomplete'}}
        response = self.client.post(self.register_url, data, format='json')
        self.assertNotEqual(response.status_code, 201)

    def test_duplicate_username(self):
        User.objects.create_user(username='duplicate', email='test1@test.com', password='pass')
        data = {
            'user': {
                'username': 'duplicate',
                'email': 'test2@test.com',
                'password': 'pass'
            },
            'grade': 5
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertNotEqual(response.status_code, 201)


class UserAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        Student.objects.create(user=self.user, grade=5)

    def test_login_success(self):
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        data = {'username': 'testuser', 'password': 'wrongpass'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_login_invalid_username(self):
        data = {'username': 'nonexistent', 'password': 'testpass123'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_token_refresh(self):
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint_without_token(self):
        profile_url = reverse('user_profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 401)

    def test_access_protected_endpoint_with_token(self):
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        login_response = self.client.post(self.login_url, login_data, format='json')
        token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_url = reverse('user_profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)


class UserProfileTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        Student.objects.create(user=self.user, grade=5)

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_get_profile(self):
        profile_url = reverse('user_profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['first_name'], 'Test')

    def test_update_profile(self):
        profile_url = reverse('user_profile')
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.put(profile_url, data, format='json')
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')


class StudentDashboardTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='pass'
        )
        self.student = Student.objects.create(user=self.user, grade=7)

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_student_dashboard_data(self):
        dashboard_url = reverse('student_dashboard')
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['student']['grade'], 7)
        self.assertIn('subjects', response.data)
        self.assertIn('total_quiz_attempts', response.data)
        self.assertIn('ai_tutor_sessions', response.data)
