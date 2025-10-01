from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import os

# create your models here

# role choices
ROLE_CHOICES = [
    ('student', 'Student'),
    ('teacher', 'Teacher')
]

# create custom user model for Users
class CustomUser(AbstractUser):
    # additional fields for user
    full_name = models.CharField(max_length=255, blank=False, null=False)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        if not self.full_name:
            raise ValidationError('Full name is required.')
        super().clean()

    def __str__(self):
        return self.username
    

# model for courses
class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses', limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

# model for course feedback
class Feedback(models.Model):
    comment = models.TextField(blank=False, null=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback', db_index=True)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedback', limit_choices_to={'role': 'student'}, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.student.full_name} on {self.course.title}"
    

# model for enrollment
class Enrolment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollment')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollment', limit_choices_to={'role': 'student'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Student: {self.student.full_name} enrolled in course: {self.course.title}"
    

# model for blocking student from enrolling to a course
class Blocked(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='blocked')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked', limit_choices_to={'role': 'student'})
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# model for notifications
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notification')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# function to validate material input
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # Get the extension
    valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Only PDF, DOC, DOCX, PPT, and PPTX files are allowed.')

# model for material    
class Material(models.Model):
    file = models.FileField(
        upload_to='course_materials/', 
        blank=False, 
        null=False,
        validators=[validate_file_extension]
    )
    description = models.TextField(blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='material')
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='material')


# model for chat history
class ChatMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"