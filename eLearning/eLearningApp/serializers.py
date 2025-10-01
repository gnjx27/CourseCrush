from rest_framework import serializers
from .models import *

# serializer for login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# serializer for custom user model
class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'photo', 'role', 'status', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password) # hash password
        user.save()
        return user
    

# serializer for course
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'created_at']
        # make teacher read only
        read_only_fields = ['teacher']


# serializer for feedback
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'comment', 'course', 'student', 'created_at']
        # make student read only
        read_only_fields = ['student']


# serializer for enrollment
class EnrolmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrolment
        fields = ['id', 'course', 'student', 'created_at']
        # make student read only
        read_only_fields = ['student']


# serializer for blocked
class BlockedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blocked
        fields = ['id', 'course', 'student', 'reason', 'created_at']


# serializer for notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at'] 


# serializer for material
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'file', 'description', 'course', 'created_at', 'teacher']
        # make teacher read only
        read_only_fields = ['teacher']


# serializer for chat message
class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['message', 'username', 'created_at']