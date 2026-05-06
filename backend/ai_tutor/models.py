from django.db import models
from users.models import Student
import uuid

class TutorSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    language = models.CharField(max_length=5, choices=[('en', 'English'), ('kn', 'Kannada')], default='en')
    title = models.CharField(max_length=200, blank=True)
    message_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.username} - {self.subject} ({self.language})"


class SessionMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=[('student', 'Student'), ('tutor', 'Tutor')])
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role} - {self.content[:50]}"


class ConversationMetrics(models.Model):
    session = models.OneToOneField(TutorSession, on_delete=models.CASCADE, related_name='metrics')
    total_tokens = models.IntegerField(default=0)
    response_time = models.FloatField(default=0.0)
    question_count = models.IntegerField(default=0)
    response_count = models.IntegerField(default=0)
    topics_discussed = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metrics for {self.session}"
