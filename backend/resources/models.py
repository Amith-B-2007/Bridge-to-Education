from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

SUBJECTS = [
    ('kannada', 'Kannada'),
    ('hindi', 'Hindi'),
    ('marathi', 'Marathi'),
    ('english', 'English'),
    ('maths', 'Mathematics'),
    ('science', 'Science'),
    ('social_science', 'Social Science'),
]

RESOURCE_TYPES = [
    ('lesson', 'Lesson'),
    ('pdf', 'PDF Notes'),
    ('video', 'Video'),
    ('notes', 'Handwritten Notes'),
    ('exercise', 'Exercise/Practice'),
]

class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True, choices=SUBJECTS)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()

class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    chapter_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    learning_objectives = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['grade', 'subject', 'chapter_number']
        unique_together = ('subject', 'grade', 'chapter_number')
        indexes = [
            models.Index(fields=['subject', 'grade']),
        ]

    def __str__(self):
        return f"{self.subject.get_name_display()} - Grade {self.grade} - Chapter {self.chapter_number}"

class Resource(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='lesson')
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    subject = models.CharField(max_length=50, choices=SUBJECTS)
    uploaded_by = models.ForeignKey('users.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.BigIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['grade', 'subject']),
        ]

class StudentResourceDownload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('users.Student', on_delete=models.CASCADE, related_name='downloaded_resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    is_offline_cached = models.BooleanField(default=False)

    class Meta:
        ordering = ['-downloaded_at']
        unique_together = ('student', 'resource')
