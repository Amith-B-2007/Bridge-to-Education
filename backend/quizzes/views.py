from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
import json
from .models import Quiz, Question, StudentQuizAttempt, QuizFeedback
from .serializers import (
    QuizSerializer, QuizDetailSerializer, QuestionSerializer,
    StudentQuizAttemptSerializer, SubmitQuizSerializer, QuizFeedbackSerializer
)
from notifications.tasks import send_quiz_notification

class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Quiz.objects.filter(is_published=True)
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade', 'subject', 'chapter']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'avg_score']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        student = request.user.student_profile
        
        serializer = SubmitQuizSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        answers = serializer.validated_data['answers_json']
        
        # Check if student already attempted this quiz
        attempt = StudentQuizAttempt.objects.filter(student=student, quiz=quiz).first()
        if not attempt:
            attempt = StudentQuizAttempt.objects.create(
                student=student,
                quiz=quiz,
                answers_json=answers,
                started_at=timezone.now()
            )
        else:
            attempt.answers_json = answers
        
        # Auto-grade the quiz
        attempt.submitted_at = timezone.now()
        attempt.is_submitted = True
        attempt.calculate_score()
        attempt.save()
        
        # Update quiz stats
        quiz.attempts += 1
        all_attempts = StudentQuizAttempt.objects.filter(quiz=quiz, is_submitted=True)
        quiz.avg_score = all_attempts.aggregate(models.Avg('percentage'))['percentage__avg'] or 0
        quiz.save()
        
        # Update student stats
        student.total_quiz_attempts += 1
        student.save()
        
        # Send SMS notification to parent
        if hasattr(student.user, 'parent_profile'):
            parent = student.user.parent_profile
            if parent.registered_phone and parent.sms_notifications_enabled:
                send_quiz_notification.delay(
                    parent.registered_phone,
                    student.user.get_full_name(),
                    int(attempt.score),
                    int(attempt.total_marks),
                    quiz.subject,
                    attempt.submitted_at.strftime('%Y-%m-%d')
                )
        
        return Response({
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'percentage': attempt.percentage,
            'passed': attempt.passed,
            'feedback': 'Quiz submitted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_attempts(self, request):
        student = request.user.student_profile
        attempts = StudentQuizAttempt.objects.filter(student=student).order_by('-submitted_at')
        serializer = StudentQuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)

from django.db import models
