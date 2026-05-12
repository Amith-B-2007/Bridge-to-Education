from django.urls import path
from . import views

app_name = "study_hub"

urlpatterns = [
    path("generate/", views.generate_lesson, name="generate"),
    path("recent/", views.recent_lessons, name="recent"),
]
