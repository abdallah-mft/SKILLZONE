from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.core.exceptions import ValidationError
from courses.models import Course, Lesson, UnlockedCourse, UserCourseProgress
from django.contrib.auth import get_user_model
from users.models import Profile
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from courses.models import Course
import io
from PIL import Image

class CourseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        pass

    def test_hard_course_validation(self):
        """Test that HARD courses require points"""
        with self.assertRaises(ValidationError):
            Course.objects.create(
                title="Test Course",
                description="Test Description",
                course_type="HARD",
                points_required=0
            )

    def test_valid_course_creation(self):
        """Test valid course creation"""
        course = Course.objects.create(
            title="Valid Course",
            description="Test Description",
            course_type="HARD",
            points_required=1000,
            points=200,  # Changed from points_reward
            rating="4.5",  # Changed to string
            price="99.99",  # Changed to string
            difficulty_level="BEGINNER"
        )
        self.assertEqual(course.title, "Valid Course")
        self.assertEqual(course.points_required, 1000)
        self.assertEqual(course.points, 200)
        self.assertEqual(course.rating, "4.5")
        self.assertEqual(course.price, "99.99")

    def test_soft_course_creation(self):
        """Test that SOFT courses don't require points"""
        course = Course.objects.create(
            title="Soft Course",
            description="Test Description",
            course_type="SOFT",
            points_required=0,
            difficulty_level="BEGINNER"
        )
        self.assertEqual(course.course_type, "SOFT")
        self.assertEqual(course.points_required, 0)

    def test_course_prerequisites(self):
        """Test course prerequisites functionality"""
        prereq_course = Course.objects.create(
            title="Prerequisite Course",
            description="Test Description",
            course_type="SOFT",
            difficulty_level="BEGINNER"
        )
        
        main_course = Course.objects.create(
            title="Main Course",
            description="Test Description",
            course_type="HARD",
            points_required=1000,
            difficulty_level="INTERMEDIATE"
        )
        
        main_course.prerequisites.add(prereq_course)
        self.assertIn(prereq_course, main_course.prerequisites.all())

class CoursePointsTestCase(TransactionTestCase):
    def setUp(self):
        # Create test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.profile = Profile.objects.get(user=self.user)
        self.profile.points = 2000
        self.profile.save()
        
        # Create test course
        self.course = Course.objects.create(
            title="Test Course",
            description="Test Description",
            course_type="HARD",
            points_required=1000,
            points_reward=500,
            difficulty_level="BEGINNER"
        )
        
        # Create test lessons
        self.lesson1 = Lesson.objects.create(
            course=self.course,
            title="Lesson 1",
            video_url="http://example.com/video1"
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course,
            title="Lesson 2",
            video_url="http://example.com/video2"
        )

    def test_course_unlock_system(self):
        """Test course unlocking and points deduction"""
        initial_points = self.profile.points
        
        # Unlock the course
        UnlockedCourse.objects.create(
            user=self.profile,
            course=self.course,
            points_spent=self.course.points_required
        )
        
        # Update user points
        self.profile.points -= self.course.points_required
        self.profile.save()
        
        # Verify points deduction
        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.points,
            initial_points - self.course.points_required
        )

    def test_course_completion_reward(self):
        """Test course completion and points reward"""
        # First unlock the course
        UnlockedCourse.objects.create(
            user=self.profile,
            course=self.course
        )
        
        initial_points = self.profile.points
        
        # Create and complete progress
        progress = CourseProgress.objects.create(
            user=self.profile,
            course=self.course
        )
        progress.completed_lessons.add(self.lesson1, self.lesson2)
        
        # Award points
        self.profile.points += self.course.points
        self.profile.save()
        
        # Verify points reward
        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.points,
            initial_points + self.course.points
        )

class CourseUploadTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = get_user_model().objects.create_user(
            username='adminuser',
            password='adminpass123',
            is_staff=True
        )
        
        # Create regular user (for permission testing)
        self.regular_user = get_user_model().objects.create_user(
            username='regularuser',
            password='userpass123'
        )
        
        # Set up API client
        self.client = APIClient()
        
    def generate_test_image(self):
        # Create a simple test image
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file
        
    def test_upload_course_success(self):
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Prepare course data
        course_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'course_type': 'SOFT',
            'difficulty_level': 'BEGINNER',
            'points_required': 0,
            'points_reward': 100,
            'duration': 60,
            'category': 'Testing',
            'tags': 'test,api,django',
            'image': self.generate_test_image(),
            'lessons': '[{"title": "Lesson 1", "duration": 15, "video_url": "https://example.com/video1"}]'
        }
        
        # Make request
        url = reverse('upload-course')
        response = self.client.post(url, course_data, format='multipart')
        
        # Assert response
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['success'])
        self.assertEqual(Course.objects.count(), 1)
        
    def test_upload_course_unauthorized(self):
        # Authenticate as regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Prepare minimal course data
        course_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'course_type': 'SOFT',
            'difficulty_level': 'BEGINNER'
        }
        
        # Make request
        url = reverse('upload-course')
        response = self.client.post(url, course_data, format='json')
        
        # Assert response
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.data['success'])
        self.assertEqual(Course.objects.count(), 0)
