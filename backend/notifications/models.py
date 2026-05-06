from django.db import models
from users.models import Student, Parent
import uuid


class NotificationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='notifications')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parent_notifications')
    event_type = models.CharField(max_length=50, choices=[
        ('quiz_result', 'Quiz Result'),
        ('marks_update', 'Marks Update'),
        ('doubt_resolved', 'Doubt Resolved'),
        ('attendance', 'Attendance'),
    ])
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.parent.user.username}"


class SMSLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15)
    message = models.TextField()
    api_response = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS to {self.phone} - {self.status}"
