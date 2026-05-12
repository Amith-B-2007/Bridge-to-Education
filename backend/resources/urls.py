from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet, ChapterViewSet, ResourceViewSet,
    get_resource_links, get_chapters_for_subject,
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'resources', ResourceViewSet, basename='resource')

app_name = 'resources'

urlpatterns = [
    # Dynamic NCERT + YouTube link generation (new, no file storage)
    path('links/', get_resource_links, name='resource-links'),
    path('chapters-list/', get_chapters_for_subject, name='chapters-list'),

    # Legacy viewset routes (kept for compatibility)
    path('', include(router.urls)),
]
