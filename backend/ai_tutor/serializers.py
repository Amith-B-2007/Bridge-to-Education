from rest_framework import serializers
from .models import TutorSession, SessionMessage, ConversationMetrics

class SessionMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionMessage
        fields = ('id', 'role', 'content', 'created_at')
        read_only_fields = ('id', 'created_at')

class TutorSessionSerializer(serializers.ModelSerializer):
    messages = SessionMessageSerializer(many=True, read_only=True)
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = TutorSession
        fields = ('id', 'subject', 'language', 'title', 'message_count', 'is_active', 'messages', 'metrics', 'created_at', 'updated_at')
        read_only_fields = ('id', 'message_count', 'created_at', 'updated_at')

    def get_metrics(self, obj):
        metrics = getattr(obj, 'metrics', None)
        if metrics:
            return {
                'total_tokens': metrics.total_tokens,
                'average_response_time': metrics.average_response_time_seconds,
                'student_questions': metrics.student_questions_count,
                'tutor_responses': metrics.tutor_responses_count,
                'topics_discussed': metrics.topics_discussed
            }
        return None

class CreateTutorSessionSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=50)
    language = serializers.ChoiceField(choices=[('en', 'English'), ('kn', 'Kannada')], default='en')

class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField()
