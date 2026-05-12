from rest_framework import serializers
from .models import TutorSession, SessionMessage


class SessionMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionMessage
        fields = ("id", "role", "content", "created_at")
        read_only_fields = ("id", "created_at")


class TutorSessionSerializer(serializers.ModelSerializer):
    messages = SessionMessageSerializer(many=True, read_only=True)

    class Meta:
        model = TutorSession
        fields = (
            "id", "grade", "syllabus", "subject", "chapter", "language",
            "title", "message_count", "is_active", "messages",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "message_count", "created_at", "updated_at")
