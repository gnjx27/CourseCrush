from django.urls import path
from .api import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'), # api register
    path('login/', LoginView.as_view(), name='api_login'), # api login
    path('logout/', LogoutView.as_view(), name='api_logout'), # api logout
    path('users/', UsersView.as_view(), name='api_users'), # api users
    path('user_details/', UserDetailsView.as_view(), name='api_user_details'), # api user details
    path('user_details_id/<int:pk>/', UserDetailsByIdView.as_view(), name='api_user_details_by_id'), # api user details by id
    path('courses/', CoursesView.as_view(), name='api_courses'), # api courses
    path('create_course/', CreateCourseView.as_view(), name='api_create_course'), # api create course
    path('course/<int:pk>/', CourseView.as_view(), name='api_course'), # api course
    path('feedbacks/', FeedbacksView.as_view(), name='api_feedbacks'), # api feedbacks
    path('create_feedback/', CreateFeedbackView.as_view(), name='api_create_feedback'), # api create feedback
    path('feedback/<int:pk>/', FeedbackView.as_view(), name='api_feedback'), # api feedback 
    path('enrolments/', EnrolmentsView.as_view(), name='api_enrolments'), # api enrolments
    path('create_enrolment/', CreateEnrolmentView.as_view(), name='api_create_enrolment'), # api create enrolment
    path('enrolment/<int:pk>', EnrolmentView.as_view(), name='api_enrolment'), # api enrolment
    path('blocklist/', BlockedListView.as_view(), name='api_blocklist'), # api blocklist
    path('block_student/', BlockStudentView.as_view(), name='api_block_student'), # api block student
    path('block/<int:pk>/', BlockView.as_view(), name='api_block'), # api block
    path('notifications/', NotificationsView.as_view(), name='api_notifications'), # api notifications
    path('materials/', MaterialsView.as_view(), name='api_materials'), # api materials
    path('create_material/', CreateMaterialView.as_view(), name='api_create_material'), # api create material
    path('material/<int:pk>/', MaterialView.as_view(), name='api_material'), # api material
]

