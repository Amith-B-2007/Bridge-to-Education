from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, ChapterViewSet, ResourceViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'resources', ResourceViewSet, basename='resource')

app_name = 'resources'

urlpatterns = [
    path('', include(router.urls)),
]
