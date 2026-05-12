from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, ai_generate_quiz

router = DefaultRouter()
router.register(r'', QuizViewSet, basename='quiz')

app_name = 'quizzes'

urlpatterns = [
    path('ai-generate/', ai_generate_quiz, name='ai-generate-quiz'),
    path('', include(router.urls)),
]
