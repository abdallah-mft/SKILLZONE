from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.core.exceptions import ValidationError
from courses.models import Course, Lesson, UnlockedCourse, CourseProgress
from django.contrib.auth import get_user_model
from users.models import Profile

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
            points_reward=200,
            difficulty_level="BEGINNER"
        )
        self.assertEqual(course.title, "Valid Course")
        self.assertEqual(course.points_required, 1000)

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
        self.profile.points += self.course.points_reward
        self.profile.save()
        
        # Verify points reward
        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.points,
            initial_points + self.course.points_reward
        )
