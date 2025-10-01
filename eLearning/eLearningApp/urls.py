from django.urls import path, include
from .views import *
from .api import *
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('api/', include('eLearningApp.api_urls')), # urls for drf generic api views
    path('', index, name='index'), # index
    path('register/', register, name='register'), # register
    path('login/', user_login, name='login'), # login
    path('explore/', explore, name='courses'), # courses
    path('course/<int:pk>/', course, name='course'), # course
    path('user_profile/<int:pk>/', user_profile, name='user_profile'), # user profile
]