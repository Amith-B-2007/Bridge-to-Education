"""
AI Tutor views - chapter-scoped chat.

The system prompt tells the AI to ONLY discuss the specific chapter.
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
import json

from common.ollama import chat
from .models import TutorSession, SessionMessage
from .serializers import TutorSessionSerializer

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu",
    "bn": "Bengali", "kn": "Kannada", "mr": "Marathi",
}


def build_tutor_system_prompt(grade, syllabus, subject, chapter, language):
    """The all-important guard: keeps the AI on-topic for one chapter."""
    lang = LANGUAGE_NAMES.get(language, "English")
    return f"""You are a kind and patient tutor for an Indian {grade}th grade student.
You are following the {syllabus} syllabus.
You ONLY answer questions about this specific chapter:
    Subject: {subject}
    Chapter: {chapter}

RULES:
1. Reply ONLY in {lang}.
2. If the student asks about anything OUTSIDE this chapter, gently say:
   "That's a great question! But let's focus on '{chapter}' for now."
3. Use simple words and Indian examples.
4. Break down hard ideas into small steps.
5. Be encouraging - praise effort.
6. Keep replies under 200 words unless asked for more detail.
"""


class TutorSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoints:
        GET    /api/ai-tutor/sessions/             list my sessions
        POST   /api/ai-tutor/sessions/             create a new chapter session
        GET    /api/ai-tutor/sessions/{id}/        get one session with messages
        POST   /api/ai-tutor/sessions/{id}/send_message/   send message + stream reply
    """

    serializer_class = TutorSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, "student_profile"):
            return TutorSession.objects.filter(
                student=self.request.user.student_profile, is_active=True
            )
        return TutorSession.objects.none()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)

    @action(detail=True, methods=["post"], url_path="send_message")
    def send_message(self, request, pk=None):
        """Streams the AI reply back chunk by chunk (Server-Sent Events)."""
        session = self.get_object()
        message_text = request.data.get("message", "").strip()
        if not message_text:
            return Response({"error": "Message is required"}, status=400)

        # 1. Save student's message
        SessionMessage.objects.create(session=session, role="student", content=message_text)

        # 2. Build conversation history for the AI
        history = []
        for m in session.messages.all():
            history.append({
                "role": "user" if m.role == "student" else "assistant",
                "content": m.content,
            })

        system_prompt = build_tutor_system_prompt(
            grade=session.grade,
            syllabus=session.syllabus,
            subject=session.subject,
            chapter=session.chapter,
            language=session.language,
        )

        # 3. Stream the reply
        def event_stream():
            full = ""
            try:
                for chunk in chat(messages=history, system_prompt=system_prompt, stream=True):
                    full += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            finally:
                SessionMessage.objects.create(session=session, role="tutor", content=full)
                session.message_count = session.messages.count()
                session.save(update_fields=["message_count", "updated_at"])
                yield f"data: {json.dumps({'done': True})}\n\n"

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
