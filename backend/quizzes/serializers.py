from rest_framework import serializers
from .models import Quiz, Question, StudentQuizAttempt, QuizFeedback

class QuestionSerializer(serializers.ModelSerializer):
    # Expose options_json as 'options' so the frontend key matches
    options = serializers.JSONField(source='options_json')

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'options', 'difficulty', 'marks')
        read_only_fields = ('id',)
        # correct_answer intentionally omitted for security

class QuestionDetailSerializer(serializers.ModelSerializer):
    options = serializers.JSONField(source='options_json')

    class Meta:
        model = Question
        fields = ('id', 'question_text', 'question_type', 'options', 'difficulty', 'marks', 'explanation')
        read_only_fields = ('id',)

class QuizSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    passing_percentage = serializers.FloatField()

    class Meta:
        model = Quiz
        fields = ('id', 'chapter', 'subject', 'subject_display', 'grade', 'title', 'description', 'num_questions', 'duration_minutes', 'passing_percentage', 'is_published', 'attempts', 'avg_score', 'created_at')
        read_only_fields = ('id', 'attempts', 'avg_score', 'created_at')

class QuizDetailSerializer(QuizSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta(QuizSerializer.Meta):
        # Extend parent fields to include nested questions
        fields = QuizSerializer.Meta.fields + ('questions',)

class SubmitQuizSerializer(serializers.Serializer):
    answers_json = serializers.JSONField()

class StudentQuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    subject = serializers.CharField(source='quiz.subject', read_only=True)

    class Meta:
        model = StudentQuizAttempt
        fields = ('id', 'quiz', 'quiz_title', 'subject', 'score', 'total_marks', 'percentage', 'passed', 'time_taken_seconds', 'submitted_at')
        read_only_fields = ('id', 'score', 'total_marks', 'percentage', 'passed', 'submitted_at')

class QuizFeedbackSerializer(serializers.ModelSerializer):
    attempt = StudentQuizAttemptSerializer(read_only=True)

    class Meta:
        model = QuizFeedback
        fields = ('id', 'attempt', 'feedback_json', 'created_at')
        read_only_fields = ('id', 'created_at')
