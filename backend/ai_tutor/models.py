"""
AI Tutor models - chapter-scoped chat.

A TutorSession is a conversation locked to ONE chapter. The AI is told:
"Only answer questions about <chapter>. If asked off-topic, politely redirect."

This makes the tutor focused and safer for kids.
"""
from django.db import models
from users.models import Student
import uuid


class TutorSession(models.Model):
    """One chapter-scoped chat thread."""

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("hi", "Hindi"),
        ("ta", "Tamil"),
        ("te", "Telugu"),
        ("bn", "Bengali"),
        ("kn", "Kannada"),
        ("mr", "Marathi"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    # Chapter scope - the AI must stay within this
    grade = models.IntegerField(default=5)
    syllabus = models.CharField(max_length=20, default="CBSE")
    subject = models.CharField(max_length=50)
    chapter = models.CharField(max_length=200, default="")
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default="en")

    title = models.CharField(max_length=200, blank=True)
    message_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.user.username} - {self.subject}/{self.chapter}"


class SessionMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(TutorSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(
        max_length=10, choices=[("student", "Student"), ("tutor", "Tutor")]
    )
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role} - {self.content[:50]}"


class ConversationMetrics(models.Model):
    session = models.OneToOneField(TutorSession, on_delete=models.CASCADE, related_name="metrics")
    total_tokens = models.IntegerField(default=0)
    response_time = models.FloatField(default=0.0)
    question_count = models.IntegerField(default=0)
    response_count = models.IntegerField(default=0)
    topics_discussed = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
