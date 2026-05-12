from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
import json
import re
from .models import Quiz, Question, StudentQuizAttempt, QuizFeedback
from .serializers import (
    QuizSerializer, QuizDetailSerializer, QuestionSerializer,
    StudentQuizAttemptSerializer, SubmitQuizSerializer, QuizFeedbackSerializer
)
from notifications.tasks import send_quiz_notification


# ── AI Quiz Generation ──────────────────────────────────────────────────────

_SUBJECT_DISPLAY = {
    'maths': 'Mathematics', 'science': 'Science', 'english': 'English',
    'social_science': 'Social Science', 'kannada': 'Kannada',
    'hindi': 'Hindi', 'marathi': 'Marathi',
}

def _fallback_questions(chapter_title: str, n: int = 5):
    """Minimal fallback when Ollama is offline."""
    base = [
        {
            "question": f"What is the main concept covered in '{chapter_title}'?",
            "options": ["A. A theoretical concept only",
                        "B. A practical skill only",
                        "C. Both theory and practical application",
                        "D. Neither theory nor practice"],
            "correct": 2,
            "explanation": "Most NCERT chapters combine both conceptual understanding and practical application."
        },
        {
            "question": f"Which learning approach is best for '{chapter_title}'?",
            "options": ["A. Only reading the textbook",
                        "B. Only watching videos",
                        "C. Reading, practising, and discussing",
                        "D. Memorising formulas without understanding"],
            "correct": 2,
            "explanation": "A multi-modal approach of reading, practising, and discussing gives the best results."
        },
        {
            "question": f"How many times should you revise '{chapter_title}' before an exam?",
            "options": ["A. Once is enough",
                        "B. At least 2-3 times",
                        "C. Revision is not needed",
                        "D. Only on exam day"],
            "correct": 1,
            "explanation": "Spaced repetition (2-3 revisions over days) significantly improves retention."
        },
        {
            "question": f"What should you do if you don't understand a topic in '{chapter_title}'?",
            "options": ["A. Skip it completely",
                        "B. Ask a teacher or use online resources",
                        "C. Wait until the exam",
                        "D. Only memorise the answers"],
            "correct": 1,
            "explanation": "Seeking help from teachers or online resources ensures proper understanding."
        },
        {
            "question": f"Which of these is a good study habit while learning '{chapter_title}'?",
            "options": ["A. Study for 6 hours straight without breaks",
                        "B. Study in short focused sessions with breaks",
                        "C. Study only on weekends",
                        "D. Read once and never revisit"],
            "correct": 1,
            "explanation": "Short focused study sessions with breaks (Pomodoro technique) improve concentration and retention."
        },
    ]
    return base[:n]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_generate_quiz(request):
    """
    POST /api/quizzes/ai-generate/
    Body: { grade, subject, chapter_title, chapter_number, num_questions? }
    Returns: { questions: [{question, options, correct, explanation}], source }
    """
    grade = int(request.data.get('grade', 5))
    subject = request.data.get('subject', 'maths').lower()
    chapter_title = request.data.get('chapter_title', 'Chapter')
    chapter_number = int(request.data.get('chapter_number', 1))
    num_questions = min(int(request.data.get('num_questions', 5)), 10)

    subject_display = _SUBJECT_DISPLAY.get(subject, subject.title())

    from common.ollama import chat, is_available

    if not is_available():
        return Response({
            'questions': _fallback_questions(chapter_title, num_questions),
            'source': 'fallback',
            'message': 'Ollama not running — showing sample questions. Start Ollama for AI-generated quizzes.',
        })

    prompt = (
        f"Create exactly {num_questions} multiple-choice questions for "
        f"Grade {grade} {subject_display}, Chapter {chapter_number}: \"{chapter_title}\".\n\n"
        "Reply with ONLY a valid JSON array — no text before or after it.\n\n"
        "Format:\n"
        "[\n"
        "  {\n"
        "    \"question\": \"Question text?\",\n"
        "    \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"],\n"
        "    \"correct\": 0,\n"
        "    \"explanation\": \"Brief reason why option A is correct.\"\n"
        "  }\n"
        "]\n\n"
        "Rules:\n"
        "- correct is the 0-based index of the right option (0=A, 1=B, 2=C, 3=D)\n"
        "- Each option must start with 'A. ', 'B. ', 'C. ', or 'D. '\n"
        f"- Questions must be appropriate for Grade {grade} students\n"
        "- Mix easy, medium, and hard difficulty\n"
        "- Focus on key concepts from this specific chapter"
    )

    try:
        raw = chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=(
                "You are an educational quiz generator for Indian school students. "
                "Always respond with valid JSON only. "
                "Never add any text, markdown, or explanation outside the JSON array."
            ),
            temperature=0.6,
        )

        # Extract JSON array from the response
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            questions = json.loads(match.group())
            # Ensure we have the right count
            if len(questions) >= 1:
                return Response({
                    'questions': questions[:num_questions],
                    'source': 'ai',
                    'chapter_title': chapter_title,
                    'grade': grade,
                    'subject': subject_display,
                })

        # JSON parse failed — return fallback
        return Response({
            'questions': _fallback_questions(chapter_title, num_questions),
            'source': 'fallback',
            'message': 'AI response could not be parsed — showing sample questions.',
        })

    except Exception as exc:
        return Response({
            'questions': _fallback_questions(chapter_title, num_questions),
            'source': 'fallback',
            'message': f'Quiz generation error: {exc}',
        })

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
