from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import DoubtSession, DoubtMessage
from .serializers import DoubtSessionSerializer, DoubtMessageSerializer


class DoubtSessionViewSet(viewsets.ModelViewSet):
    serializer_class = DoubtSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return DoubtSession.objects.filter(student=user.student_profile)
        elif hasattr(user, 'teacher_profile'):
            return DoubtSession.objects.all()
        return DoubtSession.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            serializer.save(student=user.student_profile)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def messages(self, request, pk=None):
        session = self.get_object()
        message_text = request.data.get('message', '')
        if not message_text:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        msg = DoubtMessage.objects.create(
            session=session,
            sender=request.user,
            message=message_text
        )
        return Response(DoubtMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        session = self.get_object()
        session.status = 'resolved'
        session.save()
        return Response(DoubtSessionSerializer(session).data)
