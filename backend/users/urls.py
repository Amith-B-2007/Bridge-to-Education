from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView, 
    StudentDashboardView
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('students/<int:student_id>/dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/', StudentDashboardView.as_view(), name='student_dashboard_current'),
]
