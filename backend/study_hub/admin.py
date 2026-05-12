from django.contrib import admin
from .models import StudyLesson, LessonView


@admin.register(StudyLesson)
class StudyLessonAdmin(admin.ModelAdmin):
    list_display = ("grade", "syllabus", "subject", "chapter", "language", "created_at")
    list_filter = ("grade", "syllabus", "language")
    search_fields = ("subject", "chapter")


@admin.register(LessonView)
class LessonViewAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "viewed_at")
