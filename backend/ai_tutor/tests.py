from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch, MagicMock
from .models import TutorSession, SessionMessage
from users.models import User, Student
import json


class TutorSessionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tutortest', password='pass')
        self.student = Student.objects.create(user=self.user, grade=7)

    def test_create_tutor_session(self):
        session = TutorSession.objects.create(
            student=self.student,
            subject='Maths',
            language='en'
        )
        self.assertEqual(session.student, self.student)
        self.assertEqual(session.subject, 'Maths')
        self.assertEqual(session.language, 'en')
        self.assertTrue(session.is_active)
        self.assertEqual(session.message_count, 0)

    def test_session_message_creation(self):
        session = TutorSession.objects.create(
            student=self.student,
            subject='English',
            language='kn'
        )

        message = SessionMessage.objects.create(
            session=session,
            role='student',
            content='How do I solve this?'
        )

        self.assertEqual(message.session, session)
        self.assertEqual(message.role, 'student')
        self.assertEqual(message.content, 'How do I solve this?')

    def test_session_message_count(self):
        session = TutorSession.objects.create(
            student=self.student,
            subject='Science',
            language='en'
        )

        SessionMessage.objects.create(session=session, role='student', content='Q1')
        SessionMessage.objects.create(session=session, role='tutor', content='A1')
        SessionMessage.objects.create(session=session, role='student', content='Q2')

        session.message_count = session.sessionmessage_set.count()
        session.save()

        self.assertEqual(session.message_count, 3)

    def test_kannada_session(self):
        session = TutorSession.objects.create(
            student=self.student,
            subject='Kannada',
            language='kn'
        )
        self.assertEqual(session.language, 'kn')

    def test_close_session(self):
        session = TutorSession.objects.create(
            student=self.student,
            subject='Maths',
            language='en'
        )
        self.assertTrue(session.is_active)

        session.is_active = False
        session.save()

        self.assertFalse(session.is_active)


class TutorAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apistudent', password='pass')
        self.student = Student.objects.create(user=self.user, grade=8)

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_create_tutor_session_api(self):
        url = '/api/ai-tutor/sessions/'
        data = {
            'subject': 'Maths',
            'language': 'en'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['subject'], 'Maths')
        self.assertEqual(response.data['language'], 'en')

    def test_list_tutor_sessions(self):
        TutorSession.objects.create(
            student=self.student, subject='Maths', language='en'
        )
        TutorSession.objects.create(
            student=self.student, subject='English', language='en'
        )

        url = '/api/ai-tutor/sessions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_session_detail(self):
        session = TutorSession.objects.create(
            student=self.student, subject='Science', language='en'
        )

        url = f'/api/ai-tutor/sessions/{session.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['subject'], 'Science')

    def test_session_language_support(self):
        url = '/api/ai-tutor/sessions/'
        data = {'subject': 'Kannada', 'language': 'kn'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['language'], 'kn')
