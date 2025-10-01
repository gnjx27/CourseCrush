from .models import *
from .factories import *
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APITestCase
import json

# Helper function to generate a random string for the username
def generate_random_username():
    return f"user{random.randint(1000, 9999)}_{random.randint(10000, 99999)}"

class UserAPITests(APITestCase):
    def setUp(self):
        # Create a user using the factory and ensure password is hashed
        self.user = CustomUserFactory(password="password123")
        self.client = APIClient()

    def test_register_user_successfully(self):
        # Create a unique username for registration to avoid conflicts
        unique_username = generate_random_username()

        # Prepare the data for registration with the new unique username
        user_data = {
            "username": unique_username,
            "email": f"{unique_username}@example.com",
            "password": "password123",  # You can set any password you want here
            "full_name": "Test User",
            "role": "student",  # Or 'teacher'
            "status": "Test status",
        }

        # Send POST request to the register endpoint
        response = self.client.post('/api/register/', user_data, format='multipart')

        # Ensure status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_duplicate_email(self):
        # Use the factory to create a user with a specific email
        CustomUserFactory(username="existinguser", email="duplicate@example.com")

        # Attempt to create another user with the same email
        user_data = {
            "username": "newuser",
            "email": "duplicate@example.com",  # Duplicate email
            "password": "password123",
            "full_name": "New User",
            "role": "teacher",
            "status": "Active",
            "photo": SimpleUploadedFile("profile.jpg", b"\xFF\xD8\xFF", content_type="image/jpeg")
        }
        
        # Send POST request with the duplicate email
        response = self.client.post('/api/register/', user_data, format='multipart')
        
        # Ensure that status code is 400 for bad request (duplicate email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_successfully(self):
        login_data = {
            'username': self.user.username,
            'password': 'password123'
        }

        # Send POST request to login endpoint
        response = self.client.post('/api/login/', login_data, format='json')

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_successfully(self):
        # Create a user using the factory
        user = CustomUserFactory()

        # Login the user
        login_data = {
            'username': user.username,
            'password': 'password123'
        }
        # The client.post method will automatically handle the session-based authentication
        response = self.client.post('/api/login/', login_data, format='json')

        # Send POST request to the logout endpoint (user should already be authenticated)
        response = self.client.post('/api/logout/', format='json')

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_users_view_authenticated(self):
        # Create a user using the factory
        user = CustomUserFactory()

        # Login the user
        self.client.login(username=user.username, password='password123')

        # Send GET request to the users endpoint
        response = self.client.get('/api/users/')

        # Check the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_users_view_unauthenticated(self):
        # Send GET request to the users endpoint without authentication
        response = self.client.get('/api/users/')

        # Check the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_details_authenticated(self):
        # Authenticate the user
        self.client.login(username=self.user.username, password="password123")
        
        # Send GET request to user details endpoint
        response = self.client.get('/api/user_details/', format='json')
        
        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_details_unauthenticated(self):
        # Send GET request without logging in
        response = self.client.get('/api/user_details/', format='json')
        
        # Check that the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_details_by_id_authenticated(self):
        # Authenticate the user
        self.client.login(username=self.user.username, password="password123")
        
        # Send GET request to user details by ID endpoint
        response = self.client.get(f'/api/user_details_id/{self.user.id}/', format='json')
        
        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_details_by_id_unauthenticated(self):
        # Send GET request without logging in
        response = self.client.get(f'/api/user_details_id/{self.user.id}/', format='json')
        
        # Check that the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseAPITests(APITestCase):
    def setUp(self):
        # Create a teacher user
        self.user = CustomUserFactory(role="teacher", password="password123")
        self.client = APIClient()

        # Create a teacher user using the factory
        self.teacher_user = CustomUserFactory(role="teacher", password="password123")
        self.student_user = CustomUserFactory(role="student", password="password123")

        # Create some courses for the teacher user
        self.course1 = CourseFactory(teacher=self.user)
        self.course2 = CourseFactory(teacher=self.user)

    def test_courses_view_authenticated(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Send GET request to the courses endpoint
        response = self.client.get('/api/courses/')
        
        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_courses_view_unauthenticated(self):
        # Send GET request to the courses endpoint without authentication
        response = self.client.get('/api/courses/')
        
        # Check that the response status is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_course_as_teacher(self):
        # Log in as a teacher
        self.client.login(username=self.teacher_user.username, password='password123')
        
        course_data = {
            'title': 'Test Course',
            'description': 'This is a test course description.',
        }

        # Send POST request to create course endpoint
        response = self.client.post('/api/create_course/', course_data, format='json')

        # Check that the course is created successfully (status 201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_course_as_student(self):
        # Log in as a student (should not be allowed to create a course)
        self.client.login(username=self.student_user.username, password='password123')
        
        course_data = {
            'title': 'Test Course',
            'description': 'This is a test course description.',
        }

        # Send POST request to create course endpoint
        response = self.client.post('/api/create_course/', course_data, format='json')

        # Check that the response status is 403 Forbidden (students should not be allowed)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_course(self):
        # Authenticate as teacher
        self.client.login(username=self.teacher_user.username, password="password123")
        
        # Send GET request to view the course
        response = self.client.get(f'/api/course/{self.course1.id}/', format='json')
        
        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course_as_teacher(self):
        # Authenticate as teacher
        self.client.login(username=self.user, password="password123")
        
        # Prepare updated course data
        updated_course_data = {
            "title": "Updated Course",
            "description": "This is the updated description",
        }
        
        # Send PUT request to update the course
        response = self.client.put(f'/api/course/{self.course1.id}/', updated_course_data, format='json')

        # Check that the response status is 200 OK (updated)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course_as_non_teacher(self):
        # Authenticate as student
        self.client.login(username=self.student_user.username, password="password123")
        
        # Prepare updated course data
        updated_course_data = {
            "title": "Updated Course",
            "description": "This is the updated description",
        }
        
        # Send PUT request to update the course
        response = self.client.put(f'/api/course/{self.course1.id}/', updated_course_data, format='json')

        # Check that the response status is 403 Forbidden (non-teachers can't update)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_course_as_teacher(self):
        # Authenticate as teacher
        self.client.login(username=self.user.username, password="password123")
        
        # Send DELETE request to delete the course
        response = self.client.delete(f'/api/course/{self.course1.id}/', format='json')

        # Check that the response status is 204 No Content (deleted)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_course_as_non_teacher(self):
        # Authenticate as student
        self.client.login(username=self.student_user.username, password="password123")
        
        # Send DELETE request to delete the course
        response = self.client.delete(f'/api/course/{self.course1.id}/', format='json')

        # Check that the response status is 403 Forbidden (non-teachers can't delete)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FeedbackAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = CustomUserFactory(role='student', password="password123")
        self.teacher = CustomUserFactory(role='teacher', password="password123")
        self.course = CourseFactory(teacher=self.teacher)
        self.feedback = FeedbackFactory(course=self.course, student=self.student)

    def test_get_feedbacks_authenticated(self):
        # Create feedback using the factory
        feedback = FeedbackFactory(student=self.student)

        # Login the student
        self.client.login(username=self.student.username, password='password123')

        # Send GET request to feedbacks endpoint
        response = self.client.get('/api/feedbacks/')

        # Check the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains the feedback data
        self.assertGreater(len(response.data), 0)
        self.assertEqual(response.data[0]['comment'], feedback.comment)

    def test_get_feedbacks_unauthenticated(self):
        # Send GET request to feedbacks endpoint without authentication
        response = self.client.get('/api/feedbacks/')

        # Check the response status code is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_feedback_authenticated(self):
        self.client.force_authenticate(user=self.student)

        # Create a feedback for the course
        feedback_data = {
            'comment': 'This is a feedback for the course.',
            'course': self.course.id,
            'student': self.student.id
        }
        
        response = self.client.post(f'/api/create_feedback/', feedback_data, format='json')
        
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the feedback data
        feedback = Feedback.objects.get(id=response.data['id'])
        self.assertEqual(feedback.comment, feedback_data['comment'])
        self.assertEqual(feedback.student, self.student)
        self.assertEqual(feedback.course, self.course)
    
    def test_create_feedback_unauthenticated(self):
        # Create a client without authentication
        client = APIClient()
        feedback_data = {
            'comment': 'This is a feedback for the course.'
        }
        
        response = client.post(f'/api/create_feedback/', feedback_data, format='json')
        
        # Verify that the response is unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_feedback_non_student(self):
        # Authenticate a non-student user (e.g., a teacher)
        self.client.force_authenticate(user=self.teacher)
        
        feedback_data = {
            'comment': 'This is a feedback for the course.'
        }
        
        response = self.client.post(f'/api/create_feedback/', feedback_data, format='json')
        
        # Verify that a non-student cannot create feedback
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_feedback_authenticated(self):
        self.client.force_authenticate(user=self.student)
        # Get the feedback for the authenticated user
        response = self.client.get(f'/api/feedback/{self.feedback.id}/')
        
        # Check if the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comment'], self.feedback.comment)

    def test_update_feedback_authenticated(self):
        self.client.force_authenticate(user=self.student)
        # Update feedback for the student
        new_comment = 'Updated feedback comment.'
        response = self.client.put(f'/api/feedback/{self.feedback.id}/', 
                                   {
                                       'comment': new_comment,
                                       'course': self.feedback.course.id, 
                                       'student': self.feedback.student.id
                                       }, format='json')
        
        # Check if the update is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()  # Refresh to get the latest data
        self.assertEqual(self.feedback.comment, new_comment)

    def test_update_feedback_permission_denied(self):
        # Authenticate as a different student (not the owner of the feedback)
        other_student = CustomUserFactory(role='student')
        self.client.force_authenticate(user=other_student)
        
        # Try to update feedback
        response = self.client.put(f'/api/feedback/{self.feedback.id}/', 
                                   {'comment': 'New comment'}, format='json')
        
        # Verify that the response is permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_feedback_authenticated(self):
        self.client.force_authenticate(user=self.student)
        # Delete the feedback by the owner (student)
        response = self.client.delete(f'/api/feedback/{self.feedback.id}/')
        
        # Check if the feedback is deleted successfully
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Feedback.objects.filter(id=self.feedback.id).exists())
    
    def test_delete_feedback_teacher(self):
        # Authenticate as the teacher
        self.client.force_authenticate(user=self.teacher)
        
        # Delete the feedback by the teacher (allowed)
        response = self.client.delete(f'/api/feedback/{self.feedback.id}/')
        
        # Check if the feedback is deleted successfully
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Feedback.objects.filter(id=self.feedback.id).exists())
    
    def test_delete_feedback_permission_denied(self):
        # Authenticate as a different student (not the owner of the feedback)
        other_student = CustomUserFactory(role='student')
        self.client.force_authenticate(user=other_student)
        
        # Try to delete feedback
        response = self.client.delete(f'/api/feedback/{self.feedback.id}/')
        
        # Verify that the response is permission denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class EnrolmentsViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.student = CustomUserFactory.create(role='student')
        self.client.force_authenticate(user=self.student)

        # Create some enrolments for testing
        self.enrolment1 = EnrolmentFactory.create(student=self.student)
        self.enrolment2 = EnrolmentFactory.create(student=self.student)

        # Create a teacher user
        self.teacher = CustomUserFactory.create(role='teacher')

        # Create a course taught by the teacher
        self.course = CourseFactory.create(teacher=self.teacher)

    def test_get_enrolments_authenticated(self):
        # Make a GET request to the enrolments endpoint
        response = self.client.get('/api/enrolments/')

        # Check if the status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the correct data is returned
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], self.enrolment1.id)
        self.assertEqual(response.data[1]['id'], self.enrolment2.id)

    def test_get_enrolments_not_authenticated(self):
        # Force unauthenticated request
        self.client.force_authenticate(user=None)

        # Make a GET request to the enrolments endpoint
        response = self.client.get('/api/enrolments/')

        # Check if the status code is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_enrolment_success(self):
        # Enrol the student in the course
        response = self.client.post('/api/create_enrolment/', {'course': self.course.id}, format='json')

        # Check if the status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_enrolment_already_enrolled(self):
        # Enrol the student in the course
        EnrolmentFactory.create(student=self.student, course=self.course)

        # Try to enrol the student again
        response = self.client.post('/api/create_enrolment/', {'course': self.course.id}, format='json')

        # Check if the status code is 400 Bad Request due to already being enrolled
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'You are already enrolled in this course.')
    
    def test_create_enrolment_blocked(self):
        # Block the student from the course
        BlockedFactory.create(student=self.student, course=self.course)

        # Try to enrol the student in the blocked course
        response = self.client.post('/api/create_enrolment/', {'course': self.course.id}, format='json')

        # Check if the status code is 403 Forbidden due to being blocked
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You are blocked from this course.')

    def test_create_enrolment_not_authenticated(self):
        # Force unauthenticated request
        self.client.force_authenticate(user=None)

        # Try to enrol the student (unauthenticated request)
        response = self.client.post('/api/create_enrolment/', {'course': self.course.id}, format='json')

        # Check if the status code is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_enrolment_authenticated(self):
        # Test the GET method for retrieving an enrolment
        response = self.client.get(f'/api/enrolment/{self.enrolment1.id}')

        # Check that the request is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.enrolment1.id)

    def test_delete_enrolment_teacher(self):
        # Test the DELETE method for a teacher to remove a student's enrolment
        self.client.force_authenticate(user=self.teacher)
        enrolment = EnrolmentFactory(course=self.course, student=self.student)
        
        response = self.client.delete(f'/api/enrolment/{enrolment.id}')

        # Check that the deletion is successful
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Ensure the enrolment was deleted
        self.assertFalse(Enrolment.objects.filter(id=enrolment.id).exists())
        
        # Check that a notification was created for the student
        self.assertTrue(Notification.objects.filter(user=self.student).exists())
    
    def test_delete_enrolment_not_teacher(self):
        # Test that a student cannot delete their own enrolment
        self.client.force_authenticate(user=self.student)
        
        response = self.client.delete(f'/api/enrolment/{self.enrolment1.id}')

        # Check for permission denial
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_enrolment_permission_denied(self):
        # Test that a teacher cannot delete an enrolment of a different course
        other_teacher = CustomUserFactory(role='teacher')
        other_course = CourseFactory(teacher=other_teacher)
        other_enrolment = EnrolmentFactory(course=other_course, student=self.student)

        self.client.force_authenticate(user=self.teacher)
        
        response = self.client.delete(f'/api/enrolment/{other_enrolment.id}')

        # Check for permission denied error
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestBlockedListViewTests(APITestCase):
    def setUp(self):
        # Create a teacher user and authenticate
        self.teacher = CustomUserFactory.create(role='teacher')
        self.client.force_authenticate(user=self.teacher)

        # Create a student user
        self.student = CustomUserFactory.create(role='student')

        # Create blocked records
        self.blocked1 = BlockedFactory.create(student=self.student)
        self.blocked2 = BlockedFactory.create(student=self.student)

        self.course = CourseFactory(teacher=self.teacher)
        self.enrolment = EnrolmentFactory(course=self.course, student=self.student)

    def test_get_blocked_list_authenticated_teacher(self):
        # Make a GET request to the blocked list endpoint
        response = self.client.get('/api/blocklist/')

        # Check if the status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the correct data is returned
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], self.blocked1.id)
        self.assertEqual(response.data[1]['id'], self.blocked2.id)
    
    def test_get_blocked_list_not_authenticated(self):
        # Force unauthenticated request
        self.client.force_authenticate(user=None)

        # Make a GET request to the blocked list endpoint
        response = self.client.get('/api/blocklist/')

        # Check if the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_blocked_list_as_student(self):
        # Authenticate as a student
        self.client.force_authenticate(user=self.student)

        # Make a GET request to the blocked list endpoint
        response = self.client.get('/api/blocklist/')

        # Check if the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_block_student(self):
        # Test that a teacher can block a student from their course.
        self.client.force_authenticate(user=self.teacher)

        data = {"course": self.course.id, "student": self.student.id, "reason": 'test'}
        response = self.client.post("/api/block_student/", data, format="json")

        # Check if the status code is 201 created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the Blocked record exists
        self.assertTrue(Blocked.objects.filter(course=self.course, student=self.student).exists())

        # Ensure the student is removed from enrolment
        self.assertFalse(Enrolment.objects.filter(course=self.course, student=self.student).exists())

        # Ensure notification was created
        notification = Notification.objects.filter(user=self.student).first()
        self.assertIsNotNone(notification)
        self.assertIn(f'You have been removed/blocked from course: {self.course}', notification.message)

    def test_other_teacher_cannot_block_student(self):
        # Test that a teacher who does not own the course cannot block students.
        self.other_teacher = CustomUserFactory.create(role='teacher')
        self.client.force_authenticate(user=self.other_teacher)

        data = {"course": self.course.id, "student": self.student.id, 'reason': 'test'}
        response = self.client.post("/api/block_student/", data, format="json")

        # Check if the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure no Blocked record was created
        self.assertFalse(Blocked.objects.filter(course=self.course, student=self.student).exists())

    def test_unauthenticated_user_cannot_block_student(self):
        self.client.force_authenticate(user=None)
        # Test that an unauthenticated user cannot block students.
        data = {"course": self.course.id, "student": self.student.id, 'reason': 'test'}
        response = self.client.post("/api/block_student/", data, format="json")

        # Check if the status code is 403 forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure no Blocked record was created
        self.assertFalse(Blocked.objects.filter(course=self.course, student=self.student).exists())

    def test_student_cannot_block_another_student(self):
        # Test that a student cannot block another student.
        self.client.force_authenticate(user=self.student)

        data = {"course": self.course.id, "student": self.student.id}
        response = self.client.post("/api/block_student/", data, format="json")

        # Check if the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure no Blocked record was created
        self.assertFalse(Blocked.objects.filter(course=self.course, student=self.student).exists())

    def test_teacher_can_unblock_student(self):
        # Test that a teacher can unblock a student from their course
        self.client.force_authenticate(user=self.teacher)
        new_course = CourseFactory(teacher=self.teacher)
        block = BlockedFactory(course=new_course, student=self.student)

        # Make a DELETE request to unblock the student
        response = self.client.delete(f'/api/block/{block.id}/')

        # Check if the status code is 204 No Content (successful deletion)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the Blocked record is deleted
        self.assertFalse(Blocked.objects.filter(id=block.id).exists())

        # Ensure notification was created
        notification = Notification.objects.filter(user=self.student).first()
        self.assertIsNotNone(notification)
        self.assertIn(f'You have been unblocked from course: {new_course.title}', notification.message)

    def test_other_teacher_cannot_unblock_student(self):
        # Test that a teacher who does not own the course cannot unblock students
        self.other_teacher = CustomUserFactory.create(role='teacher')
        self.client.force_authenticate(user=self.other_teacher)

        # Make a DELETE request to unblock the student
        response = self.client.delete(f'/api/block/{self.blocked1.id}/')

        # Check if the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure the Blocked record is still present
        self.assertTrue(Blocked.objects.filter(id=self.blocked1.id).exists())

    def test_unauthenticated_user_cannot_unblock_student(self):
        # Test that an unauthenticated user cannot unblock students
        self.client.force_authenticate(user=None)

        # Make a DELETE request to unblock the student
        response = self.client.delete(f'/api/block/{self.blocked1.id}/')

        # Check if the status code is 403 forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure the Blocked record is still present
        self.assertTrue(Blocked.objects.filter(id=self.blocked1.id).exists())

    def test_student_cannot_unblock_themselves(self):
        # Test that a student cannot unblock themselves
        self.client.force_authenticate(user=self.student)

        # Make a DELETE request to unblock the student (self-unblock attempt)
        response = self.client.delete(f'/api/block/{self.blocked1.id}/')

        # Check if the status code is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure the Blocked record is still present
        self.assertTrue(Blocked.objects.filter(id=self.blocked1.id).exists())


class TestNotificationsView(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = CustomUserFactory.create()
        self.client.force_authenticate(user=self.user)

        # Create notifications for the authenticated user
        self.notification1 = NotificationFactory.create(user=self.user)
        self.notification2 = NotificationFactory.create(user=self.user)

        # Create a notification for another user
        self.other_user = CustomUserFactory.create()
        self.other_notification = NotificationFactory.create(user=self.other_user)

    def test_get_notifications_authenticated_user(self):
        # Make a GET request to fetch notifications
        response = self.client.get("/api/notifications/")

        # Check if the status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if only the authenticated user's notifications are returned
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], self.notification2.id)
        self.assertEqual(response.data[1]['id'], self.notification1.id)

    def test_get_notifications_unauthenticated_user(self):
        # Force unauthenticated request
        self.client.force_authenticate(user=None)

        # Make a GET request to fetch notifications
        response = self.client.get("/api/notifications/")

        # Check if the status code is 403 forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestMaterialsView(APITestCase):
    def setUp(self):
        # Create a teacher user
        self.teacher = CustomUserFactory.create(role='teacher')
        self.client.force_authenticate(user=self.teacher)

        # Create a student user
        self.student = CustomUserFactory.create(role='student')

        # Create courses and enrolments
        self.course1 = CourseFactory.create(teacher=self.teacher)
        self.course2 = CourseFactory.create(teacher=self.teacher)
        self.enrolment = EnrolmentFactory.create(course=self.course1, student=self.student)

        # Create materials
        self.material1 = MaterialFactory.create(course=self.course1, teacher=self.teacher)
        self.material2 = MaterialFactory.create(course=self.course2, teacher=self.teacher)

    def test_get_materials_as_teacher(self):
        # Ensure teacher can only see their own materials
        response = self.client.get('/api/materials/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], self.material2.id)
        self.assertEqual(response.data[1]['id'], self.material1.id)

    def test_get_materials_as_student(self):
        # Authenticate as a student
        self.client.force_authenticate(user=self.student)

        # Ensure student can only see materials from enrolled courses
        response = self.client.get('/api/materials/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.material1.id)

    def test_get_materials_not_authenticated(self):
        # Force unauthenticated request
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/materials/')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    

class TestCreateMaterialView(APITestCase):
    def setUp(self):
        # Create a teacher user
        self.teacher = CustomUserFactory.create(role='teacher')
        self.client.force_authenticate(user=self.teacher)

        # Create a student user
        self.student = CustomUserFactory.create(role='student')

        # Create a course owned by the teacher
        self.course = CourseFactory.create(teacher=self.teacher)

        # Enroll student in the course
        self.enrolment = EnrolmentFactory.create(course=self.course, student=self.student)

        # Valid file for testing
        self.valid_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")

        # API endpoint
        self.url = "/api/create_material/"

    def test_teacher_can_create_material(self):
        # Ensure a teacher can create course materials
        data = {
            "file": self.valid_file,
            "description": "Lecture notes",
            "course": self.course.id
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 1)
        self.assertEqual(Material.objects.first().teacher, self.teacher)
        
        # Ensure notification is sent to enrolled students
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().user, self.student)

    def test_student_cannot_create_material(self):
        # Authenticate as a student
        self.client.force_authenticate(user=self.student)

        data = {
            "file": self.valid_file,
            "description": "Lecture notes",
            "course": self.course.id
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Material.objects.count(), 0)

    def test_teacher_cannot_create_material_for_other_teacher_course(self):
        # Create another teacher and their course
        another_teacher = CustomUserFactory.create(role='teacher')
        another_course = CourseFactory.create(teacher=another_teacher)

        data = {
            "file": self.valid_file,
            "description": "Lecture notes",
            "course": another_course.id
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Material.objects.count(), 0)

    def test_file_extension_validation(self):
        # Invalid file extension
        invalid_file = SimpleUploadedFile("test.exe", b"file_content", content_type="application/octet-stream")

        data = {
            "file": invalid_file,
            "description": "Lecture notes",
            "course": self.course.id
        }

        response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Unsupported file extension", response.data["detail"])
        self.assertEqual(Material.objects.count(), 0)


class TestMaterialView(APITestCase):
    def setUp(self):
        # Create a teacher user
        self.teacher = CustomUserFactory.create(role='teacher')
        self.client.force_authenticate(user=self.teacher)

        # Create a student user
        self.student = CustomUserFactory.create(role='student')

        # Create a course owned by the teacher
        self.course = CourseFactory.create(teacher=self.teacher)

        # Create material for the course
        self.material = MaterialFactory.create(course=self.course, teacher=self.teacher)

        # Valid file for update testing
        self.valid_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")

        # API endpoint
        self.url = f"/api/material/{self.material.id}/"

    def test_teacher_can_retrieve_material(self):
        # Ensure a teacher can retrieve their own material
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.material.id)

    def test_student_can_retrieve_material_if_enrolled(self):
        # Enroll student in the course
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.material.id)

    def test_student_cannot_update_material(self):
        # Authenticate as student
        self.client.force_authenticate(user=self.student)

        data = {
            "description": "Updated lecture notes",
        }

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_update_their_own_material(self):
        # Prepare the updated description and a new file (simulate an update)
        new_file = SimpleUploadedFile("new_lecture_notes.pdf", b"new file content", content_type="application/pdf")
        # Ensure the owner teacher can update their material
        data = {
            "description": "Updated lecture notes",
            "file": new_file,
            "course": self.material.course.id
        }

        response = self.client.put(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.material.refresh_from_db()
        self.assertEqual(self.material.description, "Updated lecture notes")

    def test_teacher_cannot_update_other_teacher_material(self):
        # Create another teacher
        another_teacher = CustomUserFactory.create(role="teacher")

        # Authenticate as another teacher
        self.client.force_authenticate(user=another_teacher)

        data = {
            "description": "Attempted update"
        }

        response = self.client.put(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_cannot_upload_invalid_file_format(self):
        invalid_file = SimpleUploadedFile("test.exe", b"file_content", content_type="application/octet-stream")

        data = {
            "file": invalid_file,
            "description": "Updated lecture notes"
        }

        response = self.client.put(self.url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Unsupported file extension", response.data["detail"])

    def test_teacher_can_delete_their_own_material(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Material.objects.filter(id=self.material.id).exists())

    def test_teacher_cannot_delete_other_teacher_material(self):
        # Create another teacher
        another_teacher = CustomUserFactory.create(role="teacher")

        # Authenticate as another teacher
        self.client.force_authenticate(user=another_teacher)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Material.objects.filter(id=self.material.id).exists())

    def test_student_cannot_delete_material(self):
        # Authenticate as student
        self.client.force_authenticate(user=self.student)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Material.objects.filter(id=self.material.id).exists())