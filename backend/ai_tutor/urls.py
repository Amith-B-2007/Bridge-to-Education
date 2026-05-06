from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorSessionViewSet

router = DefaultRouter()
router.register(r'sessions', TutorSessionViewSet, basename='tutor_session')

app_name = 'ai_tutor'

urlpatterns = [
    path('', include(router.urls)),
]
