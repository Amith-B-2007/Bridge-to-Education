from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from resources.models import SUBJECTS
import uuid
import json

class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey('resources.Chapter', on_delete=models.CASCADE, related_name='quizzes')
    subject = models.CharField(max_length=50, choices=SUBJECTS)
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    num_questions = models.IntegerField(default=10)
    duration_minutes = models.IntegerField(default=30)
    passing_percentage = models.FloatField(default=40.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    attempts = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['grade', 'subject']),
        ]

    def __str__(self):
        return f"{self.title} ({self.subject})"

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=[('mcq', 'Multiple Choice'), ('true_false', 'True/False')], default='mcq')
    options_json = models.JSONField(default=dict)
    correct_answer = models.CharField(max_length=10)
    explanation = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='medium')
    marks = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['quiz']),
        ]

class StudentQuizAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='student_attempts')
    answers_json = models.JSONField(default=dict)
    score = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    total_marks = models.FloatField(default=10.0)
    percentage = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    passed = models.BooleanField(default=False)
    time_taken_seconds = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['student', 'quiz']),
        ]
        unique_together = ('student', 'quiz')

    def calculate_score(self):
        score = 0
        answers = json.loads(self.answers_json) if isinstance(self.answers_json, str) else self.answers_json

        for question in self.quiz.questions.all():
            answer = answers.get(str(question.id), '')
            if answer.strip().lower() == str(question.correct_answer).strip().lower():
                score += question.marks

        self.score = score
        self.total_marks = sum(q.marks for q in self.quiz.questions.all())
        self.percentage = (score / self.total_marks * 100) if self.total_marks > 0 else 0
        self.passed = self.percentage >= self.quiz.passing_percentage
        return self.score

class QuizFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField(StudentQuizAttempt, on_delete=models.CASCADE, related_name='feedback')
    feedback_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
