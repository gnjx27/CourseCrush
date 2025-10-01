from django.shortcuts import render, redirect
from .models import *
from .serializers import *
from .forms import *
from .api_urls import *
from django.urls import reverse
import requests
from pathlib import Path
from django.conf import settings

# Create your views here.


# homepage
def index(request):
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return render(request, 'teacher-homepage.html', {
                'create_course_form': CreateCourseForm,
                'edit_course_form': EditCourseForm,
                'block_student_form': BlockStudentForm,
            })
        if request.user.role == 'student':
            return render(request, 'student-homepage.html', {
                'create_course_form': CreateCourseForm,
                'edit_course_form': EditCourseForm,
            })
    return redirect('login')
    

# register page
def register(request):
    if request.method == 'POST':
        form_data = {
            'username': request.POST.get('username'),
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'role': request.POST.get('role'),
            'status': request.POST.get('status'),
            'password': request.POST.get('password')
        }

        # Get the uploaded photo
        files = {}
        if 'photo' in request.FILES:
            files['photo'] = request.FILES['photo']
        else:
            default_photo_path = Path(settings.MEDIA_ROOT) / 'user_photos' / 'default.png'
            if default_photo_path.exists():
                files['photo'] = open(default_photo_path, 'rb')
            else:
                print(f"❌ Default image not found at: {default_photo_path}")

        # Prepare data for API request
        data = {
            'username': form_data['username'],
            'full_name': form_data['full_name'],
            'email': form_data['email'],
            'role': form_data['role'],
            'status': form_data['status'],
            'password': form_data['password'],
        }

        api_url = request.build_absolute_uri(reverse('api_register'))
        response = requests.post(api_url, data=data, files=files)
        if response.status_code == 200:
            return redirect('index')
        
        print(response.content)
        return render(request, 'login.html', {'form': LoginForm, 'error': response.content})
    
    else:
        return render(request, 'register.html', {'form': RegisterForm})
    

# login page
def user_login(request):
    return render(request, 'login.html', {
            'form': LoginForm,
        })


# courses page
def explore(request):
    if request.user.is_authenticated:
        return render(request, 'explore.html')
    else:
        return redirect('login')
    

# course page
def course(request, pk):
    return render(request, 'course.html', {
        'course': pk,
        'add_material_form': AddMaterialForm,
        'edit_material_form': EditMaterialForm,
        'add_feedback_form': AddFeedbackForm,
    })


def user_profile(request, pk):
    return render(request, 'user-page.html', {
        'user_id': pk
    })