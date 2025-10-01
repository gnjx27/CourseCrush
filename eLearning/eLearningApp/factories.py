import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
from faker import Faker
from django.contrib.auth import get_user_model
from PIL import Image
import io
import random
from django.core.files import File
from django.utils.timezone import now

# Get the CustomUser model
CustomUser = get_user_model()
fake = Faker()

# Helper function to get an existing image
def get_existing_image():
    image_path = os.path.join("media", "user_photos", "rupert.jpg")  # Adjust path
    return File(open(image_path, "rb"), name="rupert.jpg")

class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    # Faker generates fake user data
    username = factory.LazyAttribute(lambda _: f"user{fake.random_number(digits=4)}")  # Random username
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")  # Generate random full name
    role = factory.Iterator(["student", "teacher"])  # Randomly choose between student and teacher
    status = factory.Faker("sentence", nb_words=5)  # Random sentence for status

    photo = factory.LazyFunction(get_existing_image)
    
    # Password for the user, set to 'password123' by default
    password = factory.PostGenerationMethodCall("set_password", "password123")  # This will hash the password


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course
    
    # Faker generates fake data for course fields
    title = factory.Faker('sentence', nb_words=4)  # Random sentence for title
    description = factory.Faker('paragraph')  # Random paragraph for description
    
    # Assign a teacher to the course (ensure the teacher is valid)
    teacher = factory.SubFactory(CustomUserFactory)  # Using the existing CustomUserFactory for teacher
    
    # created_at is auto-generated, so it can be omitted


# Factory for the Feedback model
class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback

    comment = factory.Faker('text')
    course = factory.SubFactory(CourseFactory)
    student = factory.SubFactory(CustomUserFactory, role='student')


# Factory for the Enrolment model
class EnrolmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Enrolment

    course = factory.SubFactory(CourseFactory)  # Enrolment will use a course created by CourseFactory
    student = factory.SubFactory(CustomUserFactory)


# Factory for Blocked model
class BlockedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Blocked

    # Generating a random Course and CustomUser (student) if not provided
    course = factory.SubFactory(CourseFactory)
    student = factory.SubFactory(CustomUserFactory, role='student')
    reason = factory.Faker('paragraph')


#factory for notification model
class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(CustomUserFactory)
    message = factory.Faker('sentence')
    created_at = factory.LazyFunction(now)


# factory for material
class MaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Material

    file = factory.LazyAttribute(lambda _: SimpleUploadedFile("document.pdf", b"Dummy content", content_type="application/pdf"))
    description = factory.Faker("sentence")
    course = factory.SubFactory(CourseFactory)
    teacher = factory.LazyAttribute(lambda obj: obj.course.teacher)  # Ensure teacher matches the course teacher