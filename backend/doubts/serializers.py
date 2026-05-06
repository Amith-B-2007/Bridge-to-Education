from rest_framework import serializers
from .models import DoubtSession, DoubtMessage, DoubtFile


class DoubtMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = DoubtMessage
        fields = ('id', 'sender', 'sender_name', 'message', 'created_at')
        read_only_fields = ('id', 'created_at', 'sender')


class DoubtSessionSerializer(serializers.ModelSerializer):
    messages = DoubtMessageSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source='student.user.username', read_only=True)
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)

    class Meta:
        model = DoubtSession
        fields = ('id', 'student', 'student_name', 'teacher', 'teacher_name',
                  'subject', 'description', 'status', 'messages',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'student', 'created_at', 'updated_at')


class DoubtFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoubtFile
        fields = ('id', 'session', 'file', 'uploaded_by', 'created_at')
        read_only_fields = ('id', 'created_at', 'uploaded_by')
