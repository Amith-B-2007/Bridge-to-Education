"""
Study Hub API views.

Endpoints we expose:
    POST /api/study-hub/generate/   → generate (or fetch cached) lesson
    GET  /api/study-hub/recent/     → list recently viewed lessons for the user
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.ollama import chat
from .models import StudyLesson, LessonView
from .prompts import build_lesson_prompt, build_keypoints_prompt
from .serializers import GenerateLessonInputSerializer, StudyLessonSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_lesson(request):
    """
    Returns a lesson summary for (grade, syllabus, subject, chapter, language).

    Logic:
      1. Validate the input.
      2. If we already have a cached lesson for this combo → return it.
      3. Otherwise → ask Ollama to generate it, save it, return it.
    """
    serializer = GenerateLessonInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    # Step 1 — Check the cache
    lesson, created = StudyLesson.objects.get_or_create(
        grade=data["grade"],
        syllabus=data["syllabus"],
        subject=data["subject"],
        chapter=data["chapter"],
        language=data["language"],
        defaults={"summary": "", "key_points": []},
    )

    # Step 2 — If we just created it (or somehow it has no summary), call AI
    if created or not lesson.summary:
        system_prompt, user_prompt = build_lesson_prompt(
            grade=data["grade"],
            syllabus=data["syllabus"],
            subject=data["subject"],
            chapter=data["chapter"],
            language=data["language"],
        )

        # Generate the summary text
        summary = chat(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
            temperature=0.6,
        )

        # Generate 5 key points from the summary
        kp_sys, kp_user = build_keypoints_prompt(summary, language=data["language"])
        kp_text = chat(
            messages=[{"role": "user", "content": kp_user}],
            system_prompt=kp_sys,
            temperature=0.3,
        )
        # Convert "- a\n- b\n- c" into ["a", "b", "c"]
        key_points = [
            line.lstrip("-•* ").strip()
            for line in kp_text.splitlines()
            if line.strip().startswith(("-", "•", "*"))
        ]

        lesson.summary = summary
        lesson.key_points = key_points or []
        lesson.save()

    # Step 3 — Track that this user viewed it (for analytics)
    LessonView.objects.create(student=request.user, lesson=lesson)

    return Response(StudyLessonSerializer(lesson).data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recent_lessons(request):
    """Returns the last 10 lessons this student viewed."""
    views = LessonView.objects.filter(student=request.user).select_related("lesson")[:10]
    lessons = [v.lesson for v in views]
    return Response(StudyLessonSerializer(lessons, many=True).data)
