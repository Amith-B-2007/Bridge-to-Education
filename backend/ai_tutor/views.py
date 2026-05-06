from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from .models import TutorSession, SessionMessage, ConversationMetrics
from .serializers import (
    TutorSessionSerializer, CreateTutorSessionSerializer,
    SendMessageSerializer
)
from .ollama_client import OllamaClient
import json
import logging

logger = logging.getLogger(__name__)
ollama_client = OllamaClient()

class TutorSessionViewSet(viewsets.ModelViewSet):
    serializer_class = TutorSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TutorSession.objects.filter(student=self.request.user.student_profile)

    def create(self, request, *args, **kwargs):
        serializer = CreateTutorSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student = request.user.student_profile
        session = TutorSession.objects.create(
            student=student,
            subject=serializer.validated_data['subject'],
            language=serializer.validated_data.get('language', 'en'),
            title=f"{serializer.validated_data['subject']} Session"
        )
        
        # Initialize metrics
        ConversationMetrics.objects.create(session=session)
        
        return Response(
            TutorSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request, pk=None):
        session = self.get_object()
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_text = serializer.validated_data['message']
        
        # Save student message
        SessionMessage.objects.create(
            session=session,
            role='student',
            content=message_text
        )
        
        # Get conversation history
        messages = SessionMessage.objects.filter(session=session).order_by('created_at')
        chat_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in messages[:-1]  # Exclude the message we just added
        ]
        
        # Stream response from Ollama
        def event_stream():
            try:
                response = ollama_client.query(
                    chat_history,
                    session.student.grade,
                    session.subject,
                    session.language,
                    stream=True
                )
                
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        chunk_data = json.loads(line)
                        message_chunk = chunk_data.get('message', {}).get('content', '')
                        if message_chunk:
                            full_response += message_chunk
                            yield f"data: {json.dumps({'chunk': message_chunk})}\n\n"
                
                # Save tutor response
                SessionMessage.objects.create(
                    session=session,
                    role='tutor',
                    content=full_response,
                    tokens_used=len(full_response.split())  # Rough estimate
                )
                
                # Update session
                session.message_count += 2
                session.save()
                
                # Update metrics
                metrics = session.metrics
                metrics.total_tokens += len(full_response.split())
                metrics.student_questions_count += 1
                metrics.tutor_responses_count += 1
                metrics.save()
                
            except Exception as e:
                logger.error(f'Ollama error: {str(e)}')
                yield f"data: {json.dumps({'error': 'Failed to get response from tutor'})}\n\n"
        
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def close(self, request, pk=None):
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'message': 'Session closed'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_sessions(self, request):
        sessions = self.get_queryset().filter(is_active=True)
        serializer = TutorSessionSerializer(sessions, many=True)
        return Response(serializer.data)
