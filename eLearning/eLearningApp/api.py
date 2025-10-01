from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .permissions import *
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from pathlib import Path
from django.conf import settings
import os

# api views


# register
class RegisterView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    # ensure file uploads such as photo are handled correctly
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# login
class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            # login user (session based)
            login(request, user)
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

# logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


# users
class UsersView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    def get(self, request):
        # check if user logged in
        if not request.user.is_authenticated:
            return Response({'detail': 'Must be logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        users = CustomUser.objects.filter(is_superuser=False)
        serializer = self.get_serializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    
# user details
class UserDetailsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def get(self, request):
        # check if user logged in
        if not request.user.is_authenticated:
            return Response({'detail': 'Must be logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # if user logged in return user data
        user_data = {
            'id': request.user.id,
            'username': request.user.username,
            'full_name': request.user.full_name,
            'status': request.user.status,
            'role': request.user.role,
            'photo': request.user.photo.url
        }
        return Response(user_data, status=status.HTTP_200_OK)


# user details by id
class UserDetailsByIdView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def get(self,request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

# courses
class CoursesView(generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    def get(self, request):
        # check if user logged in
        if not request.user.is_authenticated:
            return Response({'detail': 'Must be logged in.'}, status=status.HTTP_401_UNAUTHORIZED)
        courses = self.get_queryset()
        serializer = self.get_serializer(courses, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# create course
class CreateCourseView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # Only teachers can create a course
    permission_classes = [IsTeacher]

    # set teacher to current logged in user
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

# course
class CourseView(mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    # check user logged in
    permission_classes = [IsAuthenticated]

    # set permissions based on request method
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            # add teacher to permission
            self.permission_classes = [IsAuthenticated, IsTeacher]
        else:
            # no change to permission
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)   
     
    def put(self, request, *args, **kwargs):
        # Check if the logged-in teacher is the owner of the course
        course = self.get_object()
        if course.teacher != request.user:
            raise PermissionDenied("Permission denied.")
        
        # if teacher is the owner, proceed with update
        return self.update(request, *args, **kwargs)
     
    def delete(self, request, *args, **kwargs):
        # Check if the logged-in teacher is the owner of the course
        course = self.get_object()
        if course.teacher != request.user:
            raise PermissionDenied("Permission denied.")
        
        # If teacher is the owner, proceed with the deletion
        return self.destroy(request, *args, **kwargs)
    

# feedbacks
class FeedbacksView(generics.ListAPIView):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        return Feedback.objects.all().order_by('-created_at')  # Order by newest first

    def get(self, request):
        # Check if user is logged in
        if not request.user.is_authenticated:
            return Response({'detail': 'Must be logged in.'}, status=status.HTTP_401_UNAUTHORIZED)

        feedbacks = self.get_queryset()
        serializer = self.get_serializer(feedbacks, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

# create feedback
class CreateFeedbackView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    # set the student field as the currently logged in user
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


# feedback
class FeedbackView(mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin,
                   generics.GenericAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    # set permissions based on request method
    def get_permissions(self):
        if self.request.method == 'PUT':
            # only student can update feedback
            self.permission_classes = [IsAuthenticated, IsStudent]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        # get feedback
        feedback = self.get_object()
        
        # if user not owner of feedback
        if feedback.student != request.user:
            raise PermissionDenied("Permission denied.")
        
        # continue update if user is owner
        return self.update(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        # get feedback
        feedback = self.get_object()
        
        # if user is owner or teacher
        if request.user == feedback.student or request.user.role == 'teacher':
            # continue delete
            return self.destroy(request, *args, **kwargs)
        else:
            raise PermissionDenied('Permission denied.')
    

# enrolments
class EnrolmentsView(generics.ListAPIView):
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return all enrolments without filtering by user role
        return Enrolment.objects.all()

    def get(self, request, *args, **kwargs):
        enrolments = self.get_queryset()
        serializer = self.get_serializer(enrolments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

# create enrolment
class CreateEnrolmentView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer

    # only allow students to create enrolment
    permission_classes = [IsAuthenticated, IsStudent]
    
    # set the student field as the currently logged in user
    def perform_create(self, serializer):
        # get student and course
        student = self.request.user
        course = serializer.validated_data['course']

        # check if student is blocked from course
        if Blocked.objects.filter(course=course, student=student).exists():
            raise PermissionDenied('You are blocked from this course.')
        
        # check if student already enrolled in course
        if Enrolment.objects.filter(course=course, student=student).exists():
            raise ValidationError({"detail": "You are already enrolled in this course."})
        
        # save enrolment if not blocked
        serializer.save(student=student)

        # notify teacher of enrolment
        message = f'{student.full_name} has enrolled in your course: {course.title}.'
        Notification.objects.create(
            user=course.teacher,
            message=message
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# enrolment
class EnrolmentView(mixins.RetrieveModelMixin, generics.GenericAPIView, mixins.DestroyModelMixin):
    queryset = Enrolment.objects.all()
    serializer_class = EnrolmentSerializer

    # set permissions based on request method
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsTeacher]

        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        enrolment = self.get_object()
        # only teacher of course can delete enrolment
        if request.user == enrolment.course.teacher:
            # notify student of deletion
            message = f'You have been removed from course {enrolment.course.title} by {enrolment.course.teacher.full_name}.'
            Notification.objects.create(
                user=enrolment.student,
                message=message
            )
            
            # delete enrolment
            return self.destroy(request, *args, **kwargs)
        else:
            raise PermissionDenied('Permission denied.')


# blocked list
class BlockedListView(generics.ListAPIView):
    queryset = Blocked.objects.all()
    serializer_class = BlockedSerializer
    
    # only teachers can view blocked list 
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, *args, **kwargs):
        blocklist = self.get_queryset()
        serializer = self.get_serializer(blocklist, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# block student
class BlockStudentView(generics.GenericAPIView, mixins.CreateModelMixin):
    queryset = Blocked.objects.all()
    serializer_class = BlockedSerializer

    # only teachers can block students
    permission_classes = [IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        # get course and student
        course = serializer.validated_data['course']
        student = serializer.validated_data['student']
        
        if course.teacher != self.request.user:
            raise PermissionDenied('Only the owner of this course can block students.')
        
        # get student enrolment in course
        enrolment = Enrolment.objects.filter(course=course, student=student).first()
        
        # check if enrolment exists
        if enrolment:
            enrolment.delete()
        # save blocked record
        serializer.save()

        # notify student
        message = f'You have been removed/blocked from course: {course} by {course.teacher.full_name}.'
        Notification.objects.create(
            user=student,
            message=message
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
            
    
# unblock student
class BlockView(mixins.RetrieveModelMixin, generics.GenericAPIView, mixins.DestroyModelMixin):
    queryset = Blocked.objects.all()
    serializer_class = BlockedSerializer

    # only teachers can block students
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # get block object
        block = self.get_object()
        # check if user is owner of course
        if request.user != block.course.teacher:
            raise PermissionDenied('Only the owner of this course can unblock students.')
        
        # notify student of unblock
        message = f'You have been unblocked from course: {block.course.title} by {block.course.teacher.full_name}, You can now re-enroll in the course.'
        Notification.objects.create(
            user=block.student,
            message=message
        )
        return self.destroy(request, *args, **kwargs)


# notification for current user
class NotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    # get filtered notifications for current user
    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user).order_by('-created_at')
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

# materials
class MaterialsView(generics.ListAPIView):
    serializer_class = MaterialSerializer
    permission_classes = [IsAuthenticated]

    # get appropriate queryset based on user
    def get_queryset(self):
        user = self.request.user
        
        # if user is teacher
        if user.role == 'teacher':
            return Material.objects.filter(teacher=user).order_by('-created_at')
        # if user is student
        elif user.role == 'student':
            # get courses current user is enrolled in
            enrolled_courses = Enrolment.objects.filter(student=user).values_list('course', flat=True)

            # return materials for those courses
            return Material.objects.filter(course__in=enrolled_courses).order_by('-created_at')
        
        return Material.objects.none()
        
        
# create material
class CreateMaterialView(mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    # only teachers can create material
    permission_classes = [IsTeacher]

    def perform_create(self, serializer):
        user = self.request.user
        # ensure that user is teacher
        if user.role != 'teacher':
            raise PermissionDenied('Only teachers can create materials')
        
        # ensure user owns material
        course = serializer.validated_data.get('course')
        if course.teacher != user:
            raise PermissionDenied('Only the owner of the course can create material for it.')
        
        # assign teacher to material
        material = serializer.save(teacher=user)
        
        # fetch students enrolled in course for this material
        enrolled_students = Enrolment.objects.filter(course=material.course).values_list('student', flat=True)

        message = f'New material has been uploaded for course: {material.course.title}.'

        # send notifications to each of the students
        for student_id in enrolled_students:
            # retrieve student by id
            student = CustomUser.objects.get(id=student_id)
            Notification.objects.create(
                user=student,
                message=message
            )

    def post(self, request, *args, **kwargs):
        # Validate file type before processing
        file = request.FILES.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
            if ext not in valid_extensions:
                return Response(
                    {'detail': 'Unsupported file extension. Only PDF, DOC, DOCX, PPT, and PPTX files are allowed.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return self.create(request, *args, **kwargs)


# material
class MaterialView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    
    # set permissions based on request method
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            # only teacher can update and delete material
            self.permission_classes = [IsAuthenticated, IsTeacher]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)   
     
    def put(self, request, *args, **kwargs):
        # Check if the logged-in teacher is the owner of the material
        material = self.get_object()
        if material.teacher != request.user:
            raise PermissionDenied("Only the owner of this material can edit it.")

        # Validate file type before processing
        file = request.FILES.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
            if ext not in valid_extensions:
                return Response(
                    {'detail': 'Unsupported file extension. Only PDF, DOC, DOCX, PPT, and PPTX files are allowed.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Delete old file if a new one is being uploaded
            file_path = Path(settings.MEDIA_ROOT) / material.file.name
            if file_path.exists():
                file_path.unlink()
        else:
            # if no new file added use existing file
            request.data._mutable = True
            request.data['file'] = material.file
            request.data._mutable = False

        # if user is the owner, proceed with update
        return self.update(request, *args, **kwargs)
     
    def delete(self, request, *args, **kwargs):
        # Check if the logged-in teacher is the owner of the material
        material = self.get_object()
        if material.teacher != request.user:
            raise PermissionDenied("Only the owner of this material can delete it.")
        
        # Build the file path using MEDIA_ROOT and material file name
        if material.file:
            file_path = Path(settings.MEDIA_ROOT) / material.file.name
            
            # Delete the file if it exists
            if file_path.exists():
                file_path.unlink()  # Delete the file

        # If user is the owner, proceed with the deletion of the material record
        return self.destroy(request, *args, **kwargs)

    