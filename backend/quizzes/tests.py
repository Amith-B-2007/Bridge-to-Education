from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Quiz, Question, StudentQuizAttempt, Chapter
from users.models import User, Student
from resources.models import Subject
import json


class QuizGradingTestCase(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name='Maths')
        self.chapter = Chapter.objects.create(
            subject=self.subject,
            grade=7,
            chapter_number=1,
            title='Basic Arithmetic'
        )
        self.quiz = Quiz.objects.create(
            chapter=self.chapter,
            subject=self.subject,
            grade=7,
            title='Test Quiz',
            num_questions=3,
            duration_minutes=30
        )

        self.q1 = Question.objects.create(
            quiz=self.quiz,
            question_text='What is 2+2?',
            question_type='mcq',
            options_json={'a': '3', 'b': '4', 'c': '5', 'd': '6'},
            correct_answer='b',
            marks=1
        )
        self.q2 = Question.objects.create(
            quiz=self.quiz,
            question_text='Is 5 > 3?',
            question_type='true_false',
            options_json={'true': 'True', 'false': 'False'},
            correct_answer='true',
            marks=1
        )
        self.q3 = Question.objects.create(
            quiz=self.quiz,
            question_text='10 - 3 = ?',
            question_type='mcq',
            options_json={'a': '5', 'b': '6', 'c': '7', 'd': '8'},
            correct_answer='c',
            marks=1
        )

    def test_perfect_score(self):
        user = User.objects.create_user(username='student1', password='pass')
        student = Student.objects.create(user=user, grade=7)

        attempt = StudentQuizAttempt.objects.create(
            student=student,
            quiz=self.quiz,
            answers_json={'0': 'b', '1': 'true', '2': 'c'}
        )
        attempt.calculate_score()

        self.assertEqual(attempt.score, 3)
        self.assertEqual(attempt.total_marks, 3)
        self.assertEqual(attempt.percentage, 100)
        self.assertTrue(attempt.passed)

    def test_partial_score(self):
        user = User.objects.create_user(username='student2', password='pass')
        student = Student.objects.create(user=user, grade=7)

        attempt = StudentQuizAttempt.objects.create(
            student=student,
            quiz=self.quiz,
            answers_json={'0': 'b', '1': 'false', '2': 'c'}
        )
        attempt.calculate_score()

        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.percentage, 66)

    def test_zero_score(self):
        user = User.objects.create_user(username='student3', password='pass')
        student = Student.objects.create(user=user, grade=7)

        attempt = StudentQuizAttempt.objects.create(
            student=student,
            quiz=self.quiz,
            answers_json={'0': 'a', '1': 'false', '2': 'a'}
        )
        attempt.calculate_score()

        self.assertEqual(attempt.score, 0)
        self.assertEqual(attempt.percentage, 0)
        self.assertFalse(attempt.passed)

    def test_unique_quiz_attempt_per_student(self):
        user = User.objects.create_user(username='student4', password='pass')
        student = Student.objects.create(user=user, grade=7)

        attempt1 = StudentQuizAttempt.objects.create(
            student=student,
            quiz=self.quiz,
            answers_json={'0': 'b', '1': 'true', '2': 'c'}
        )

        attempt2 = StudentQuizAttempt(
            student=student,
            quiz=self.quiz,
            answers_json={'0': 'a', '1': 'false', '2': 'a'}
        )
        with self.assertRaises(Exception):
            attempt2.save()


class QuizAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(name='English')
        self.chapter = Chapter.objects.create(
            subject=self.subject,
            grade=6,
            chapter_number=2,
            title='Grammar Basics'
        )
        self.quiz = Quiz.objects.create(
            chapter=self.chapter,
            subject=self.subject,
            grade=6,
            title='Grammar Quiz',
            num_questions=2,
            is_published=True
        )

        Question.objects.create(
            quiz=self.quiz,
            question_text='Which is correct?',
            question_type='mcq',
            options_json={'a': 'He go', 'b': 'He goes', 'c': 'He going', 'd': 'He gone'},
            correct_answer='b',
            marks=1
        )
        Question.objects.create(
            quiz=self.quiz,
            question_text='Plural of "child" is "children"',
            question_type='true_false',
            options_json={'true': 'True', 'false': 'False'},
            correct_answer='true',
            marks=1
        )

        self.user = User.objects.create_user(username='quizstudent', password='pass')
        self.student = Student.objects.create(user=self.user, grade=6)

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_list_quizzes(self):
        url = f'/api/quizzes/?grade=6&subject=English'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)

    def test_get_quiz_detail(self):
        url = f'/api/quizzes/{self.quiz.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Grammar Quiz')
        self.assertEqual(len(response.data['questions']), 2)

    def test_submit_quiz(self):
        url = f'/api/quizzes/{self.quiz.id}/submit/'
        data = {
            'answers': {'0': 'b', '1': 'true'}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['score'], 2)
        self.assertEqual(response.data['percentage'], 100)
        self.assertTrue(response.data['passed'])

    def test_submit_quiz_twice_fails(self):
        url = f'/api/quizzes/{self.quiz.id}/submit/'
        data = {'answers': {'0': 'b', '1': 'true'}}

        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.post(url, data, format='json')
        self.assertNotEqual(response2.status_code, 200)

    def test_quiz_history(self):
        submit_url = f'/api/quizzes/{self.quiz.id}/submit/'
        self.client.post(submit_url, {'answers': {'0': 'b', '1': 'true'}}, format='json')

        history_url = '/api/students/quizzes/history/'
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)


class QuizFilteringTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        maths = Subject.objects.create(name='Maths')
        science = Subject.objects.create(name='Science')

        maths_ch1 = Chapter.objects.create(
            subject=maths, grade=5, chapter_number=1, title='Numbers'
        )
        maths_ch2 = Chapter.objects.create(
            subject=maths, grade=6, chapter_number=1, title='Algebra'
        )
        science_ch1 = Chapter.objects.create(
            subject=science, grade=5, chapter_number=1, title='Life Sciences'
        )

        Quiz.objects.create(
            chapter=maths_ch1, subject=maths, grade=5, title='Numbers Quiz', is_published=True
        )
        Quiz.objects.create(
            chapter=maths_ch2, subject=maths, grade=6, title='Algebra Quiz', is_published=True
        )
        Quiz.objects.create(
            chapter=science_ch1, subject=science, grade=5, title='Science Quiz', is_published=True
        )

    def test_filter_by_grade(self):
        response = self.client.get('/api/quizzes/?grade=5')
        self.assertEqual(response.status_code, 200)
        for quiz in response.data['results']:
            self.assertEqual(quiz['grade'], 5)

    def test_filter_by_subject(self):
        response = self.client.get('/api/quizzes/?subject=Maths')
        self.assertEqual(response.status_code, 200)
        for quiz in response.data['results']:
            self.assertEqual(quiz['subject_name'], 'Maths')

    def test_filter_by_grade_and_subject(self):
        response = self.client.get('/api/quizzes/?grade=5&subject=Maths')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)
        for quiz in response.data['results']:
            self.assertEqual(quiz['grade'], 5)
            self.assertEqual(quiz['subject_name'], 'Maths')
