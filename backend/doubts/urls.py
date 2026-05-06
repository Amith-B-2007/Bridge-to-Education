from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoubtSessionViewSet

router = DefaultRouter()
router.register(r'sessions', DoubtSessionViewSet, basename='doubt-session')

app_name = 'doubts'

urlpatterns = [
    path('', include(router.urls)),
]
