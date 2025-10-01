from django import forms
from .models import *

# register form
class RegisterForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'email', 'photo', 'role', 'status', 'password']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'role': forms.Select(attrs={'class': 'form-control', 'id': 'role'}),  # Assuming 'role' is a choice field
            'status': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off', 'id': 'status'}),  # Adjust if 'status' is a choice field or different type
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


# login form
class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']

        widgets = {
            'username': forms.TextInput(attrs={'id': 'login-username', 'class': 'form-control', 'autocomplete': 'off'}),
            'password': forms.PasswordInput(attrs={'id': 'login-password', 'class': 'form-control'}),
        }


# create course form
class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

        widgets = {
            'title': forms.TextInput(attrs={'id': 'create-course-title', 'class': 'form-control', 'autocomplete': 'off'}),
            'description': forms.TextInput(attrs={'id': 'create-course-description', 'class': 'form-control', 'autocomplete': 'off'})
        }


# edit course form
class EditCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

        widgets = {
            'title': forms.TextInput(attrs={'id': 'edit-course-title-${course.id}', 'class': 'form-control', 'autocomplete': 'off', 'value': '${course.title}'}),
            'description': forms.TextInput(attrs={'id': 'edit-course-description-${course.id}', 'class': 'form-control', 'autocomplete': 'off', 'value': '${course.description}'})
        }
        

# add material form
class AddMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['file', 'description']

        widgets = {
            'file': forms.FileInput(attrs={'id': 'add-material-file', 'class': 'form-control', 'name':'file', 'accept':'.pdf,.doc,.docx,.ppt,.pptx'}),
            'description': forms.TextInput(attrs={'id': 'add-material-description', 'class': 'form-control', 'autocomplete': 'off'})
        }


# edit material form
class EditMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['file', 'description']

        widgets = {
            'file': forms.FileInput(attrs={'id': 'edit-material-file-${material.id}', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'id': 'edit-material-description-${material.id}', 'class': 'form-control', 'autocomplete': 'off', 'value': '${material.description}'})
        }


# block student form
class BlockStudentForm(forms.ModelForm):
    class Meta:
        model = Blocked
        fields = ['course', 'student', 'reason']

        widgets = {
            'course': forms.Select(attrs={'id': 'block-student-course', 'class': 'form-control'}),
            'student': forms.Select(attrs={'id': 'block-student-student', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'id': 'block-student-reason', 'class': 'form-control', 'rows': 3}),
        }


# add feedback form
class AddFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['comment']
        
        widgets = {
            'comment': forms.Textarea(attrs={'id': 'feedback-comment', 'class': 'form-control'}),
        }