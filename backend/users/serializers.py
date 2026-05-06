from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError
from .models import Student, Teacher, Mentor, Parent

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'school_name', 'profile_pic', 'created_at')
        read_only_fields = ('id', 'created_at')

class StudentRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Student
        fields = ('user', 'grade', 'password', 'password_confirm')

    def validate(self, data):
        if data.get('password') != data.pop('password_confirm', None):
            raise ValidationError({'password': 'Passwords do not match'})
        
        # Check if username already exists
        username = data['user'].get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken'})
        
        # Check if email already exists
        email = data['user'].get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already registered'})
        
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        
        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email', ''),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            phone=user_data.get('phone'),
            school_name=user_data.get('school_name'),
            password=password
        )
        user.role = 'student'
        user.save()
        
        student = Student.objects.create(user=user, **validated_data)
        return student

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'user', 'grade', 'assigned_mentor', 'subjects_interested', 'total_sessions', 'total_quiz_attempts', 'attendance', 'created_at')
        read_only_fields = ('id', 'total_sessions', 'total_quiz_attempts', 'created_at')

class TeacherRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Teacher
        fields = ('user', 'assigned_grades', 'assigned_subjects', 'password', 'password_confirm')

    def validate(self, data):
        if data.get('password') != data.pop('password_confirm', None):
            raise ValidationError({'password': 'Passwords do not match'})
        
        # Check if username already exists
        username = data['user'].get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError({'username': 'This username is already taken'})
        
        # Check if email already exists
        email = data['user'].get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError({'email': 'This email is already registered'})
        
        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        
        # Remove None values
        user_data = {k: v for k, v in user_data.items() if v is not None}
        
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email', ''),
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            phone=user_data.get('phone'),
            school_name=user_data.get('school_name'),
            password=password
        )
        user.role = 'teacher'
        user.save()
        
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = ('id', 'user', 'assigned_grades', 'assigned_subjects', 'bio', 'qualification', 'resources_uploaded', 'created_at')
        read_only_fields = ('id', 'resources_uploaded', 'created_at')

class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Parent
        fields = ('id', 'user', 'registered_phone', 'associated_students', 'preferred_language', 'sms_notifications_enabled', 'created_at')
        read_only_fields = ('id', 'created_at')

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise ValidationError('Invalid credentials')
        data['user'] = user
        return data
