from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Subject, Chapter, Resource, StudentResourceDownload
from .serializers import (
    SubjectSerializer, ChapterSerializer, ResourceSerializer,
    ResourceUploadSerializer, StudentResourceDownloadSerializer
)

class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['subject', 'grade']
    ordering = ['grade', 'chapter_number']

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.filter(is_approved=True)
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade', 'subject', 'resource_type', 'chapter']
    search_fields = ['title', 'description']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return ResourceUploadSerializer
        return ResourceSerializer

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {'error': 'Only teachers can upload resources'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resource = serializer.save(
            uploaded_by=request.user.teacher_profile,
            is_approved=True  # Auto-approve for now
        )
        
        return Response(
            ResourceSerializer(resource).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        resource = self.get_object()
        student = request.user.student_profile
        
        download, created = StudentResourceDownload.objects.get_or_create(
            student=student,
            resource=resource
        )
        
        # Increment download count
        resource.download_count += 1
        resource.save()
        
        return Response({
            'message': 'Resource downloaded',
            'file_path': resource.file_path,
            'file_size': resource.file_size
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_downloads(self, request):
        student = request.user.student_profile
        downloads = StudentResourceDownload.objects.filter(student=student).order_by('-downloaded_at')
        serializer = StudentResourceDownloadSerializer(downloads, many=True)
        return Response(serializer.data)
