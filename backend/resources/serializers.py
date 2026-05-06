from rest_framework import serializers
from .models import Subject, Chapter, Resource, StudentResourceDownload

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description', 'icon')

class ChapterSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)

    class Meta:
        model = Chapter
        fields = ('id', 'subject', 'subject_display', 'grade', 'chapter_number', 'title', 'description', 'learning_objectives', 'created_at')
        read_only_fields = ('id', 'created_at')

class ResourceSerializer(serializers.ModelSerializer):
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.user.get_full_name', read_only=True)

    class Meta:
        model = Resource
        fields = ('id', 'chapter', 'title', 'description', 'resource_type', 'resource_type_display', 'grade', 'subject', 'subject_display', 'uploaded_by', 'uploaded_by_name', 'file_path', 'file_size', 'is_approved', 'download_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'download_count', 'created_at', 'updated_at')

class ResourceUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('chapter', 'title', 'description', 'resource_type', 'grade', 'subject', 'file_path')

class StudentResourceDownloadSerializer(serializers.ModelSerializer):
    resource = ResourceSerializer(read_only=True)

    class Meta:
        model = StudentResourceDownload
        fields = ('id', 'resource', 'downloaded_at', 'is_offline_cached')
        read_only_fields = ('id', 'downloaded_at')
