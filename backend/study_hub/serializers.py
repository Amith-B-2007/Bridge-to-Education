"""
Serializers convert Python objects ↔ JSON for the API.
"""
from rest_framework import serializers
from .models import StudyLesson


class GenerateLessonInputSerializer(serializers.Serializer):
    """Validates the data the frontend sends when asking for a lesson."""

    grade = serializers.IntegerField(min_value=1, max_value=10)
    syllabus = serializers.CharField(max_length=20)
    subject = serializers.CharField(max_length=80)
    chapter = serializers.CharField(max_length=200)
    language = serializers.CharField(max_length=5, default="en")


class StudyLessonSerializer(serializers.ModelSerializer):
    """Returns lesson data to the frontend."""

    class Meta:
        model = StudyLesson
        fields = [
            "id",
            "grade",
            "syllabus",
            "subject",
            "chapter",
            "language",
            "summary",
            "key_points",
            "created_at",
        ]
        read_only_fields = fields
