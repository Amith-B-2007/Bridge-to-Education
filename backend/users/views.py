from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Student, Teacher, Mentor, Parent
from .serializers import (
    UserSerializer, StudentSerializer, TeacherSerializer, 
    ParentSerializer, StudentRegistrationSerializer, 
    TeacherRegistrationSerializer, LoginSerializer
)
from quizzes.models import StudentQuizAttempt
from ai_tutor.models import TutorSession

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        role = request.data.get('role', 'student')
        
        if role == 'student':
            serializer = StudentRegistrationSerializer(data=request.data)
        elif role == 'teacher':
            serializer = TeacherRegistrationSerializer(data=request.data)
        else:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            student_or_teacher = serializer.save()
            user = student_or_teacher.user
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': f'{role.title()} registered successfully',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id=None):
        if student_id is None:
            try:
                student_id = request.user.student_profile.id
            except:
                # User is not a student, return minimal dashboard
                return Response({
                    'user': UserSerializer(request.user).data,
                    'message': f'Welcome {request.user.get_full_name() or request.user.username}'
                }, status=status.HTTP_200_OK)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get quiz stats
        quiz_attempts = StudentQuizAttempt.objects.filter(student=student, is_submitted=True)
        avg_scores = {}
        
        for subject in ['kannada', 'english', 'maths', 'science', 'social_science']:
            subject_attempts = quiz_attempts.filter(quiz__subject=subject)
            if subject_attempts.exists():
                avg_score = subject_attempts.aggregate(models.Avg('percentage'))['percentage__avg']
                avg_scores[subject] = round(avg_score, 2)
            else:
                avg_scores[subject] = 0
        
        # Get AI tutor session count
        tutor_sessions = TutorSession.objects.filter(student=student).count()
        
        return Response({
            'student': StudentSerializer(student).data,
            'subjects': {
                'Kannada': {'avg_score': avg_scores.get('kannada', 0), 'chapters_completed': 0},
                'English': {'avg_score': avg_scores.get('english', 0), 'chapters_completed': 0},
                'Maths': {'avg_score': avg_scores.get('maths', 0), 'chapters_completed': 0},
                'Science': {'avg_score': avg_scores.get('science', 0), 'chapters_completed': 0},
                'Social Science': {'avg_score': avg_scores.get('social_science', 0), 'chapters_completed': 0},
            },
            'recent_quizzes': quiz_attempts.values('quiz__title', 'percentage', 'submitted_at').order_by('-submitted_at')[:5],
            'attendance': student.attendance,
            'ai_tutor_sessions': tutor_sessions,
            'total_quiz_attempts': student.total_quiz_attempts
        })

from django.db import models


class StudentListView(APIView):
    """GET /api/users/students/ — returns all students with aggregate stats."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.all().select_related('user').order_by('-user__date_joined')
        data = []
        for student in students:
            attempts = StudentQuizAttempt.objects.filter(student=student, is_submitted=True)
            avg = attempts.aggregate(models.Avg('percentage'))['percentage__avg']
            tutor_count = TutorSession.objects.filter(student=student).count()
            data.append({
                'id': student.id,
                'username': student.user.username,
                'name': student.user.get_full_name() or student.user.username,
                'grade': student.grade,
                'attendance': round(float(student.attendance or 0), 1),
                'total_quiz_attempts': student.total_quiz_attempts,
                'avg_score': round(float(avg), 1) if avg else 0,
                'school': student.user.school_name or '',
                'subjects': student.subjects_interested or '',
                'tutor_sessions': tutor_count,
            })
        return Response({'students': data, 'count': len(data)})

