from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('mentor', 'Mentor'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True, unique=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    profile_pic = models.FileField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_permissions'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Grade level 1-10"
    )
    assigned_mentor = models.ForeignKey(
        'Mentor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students'
    )
    subjects_interested = models.CharField(
        max_length=255,
        default='',
        help_text="Comma-separated list of interested subjects"
    )
    total_sessions = models.IntegerField(default=0)
    total_quiz_attempts = models.IntegerField(default=0)
    attendance = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['grade', 'user']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - Grade {self.grade}"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    assigned_grades = models.CharField(
        max_length=255,
        default='',
        help_text="Comma-separated list of grade levels, e.g., '1,2,3'"
    )
    assigned_subjects = models.CharField(
        max_length=255,
        default='',
        help_text="Comma-separated list of subjects"
    )
    bio = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    resources_uploaded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} (Teacher)"


class Mentor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    bio = models.TextField(blank=True, null=True)
    expertise_areas = models.CharField(max_length=255, blank=True, null=True)
    total_students = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} (Mentor)"


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    registered_phone = models.CharField(
        max_length=15,
        unique=True,
        help_text="Phone number for SMS notifications"
    )
    associated_students = models.ManyToManyField(
        Student,
        related_name='parents',
        blank=True,
        help_text="Link parent to their child/children"
    )
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('kn', 'Kannada')],
        default='en'
    )
    sms_notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['registered_phone']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} (Parent)"
