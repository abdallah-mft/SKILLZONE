import pytest
from django.contrib.auth import get_user_model
from courses.models import Course, Lesson
from quizzes.models import Quiz, Question, Answer

def create_sample_courses():
    """Create sample courses with lessons and quizzes"""
    # Clear existing data
    Course.objects.all().delete()
    
    # Python Programming Course (HARD skill)
    python_course = Course.objects.create(
        title="Python Programming Fundamentals",
        description="Learn Python programming from scratch. Cover basic syntax, data structures, and OOP concepts.",
        course_type="HARD",
        points_required=50,
        category="Programming",
        tags="python,programming,beginner",
        difficulty_level="BEGINNER",
        estimated_duration=300  # 5 hours
    )
    
    # Python Course Lessons
    python_lesson1 = Lesson.objects.create(
        course=python_course,
        title="Introduction to Python",
        video_url="https://example.com/python-intro",
        points_required=0,
        points_reward=10
    )
    
    python_lesson2 = Lesson.objects.create(
        course=python_course,
        title="Variables and Data Types",
        video_url="https://example.com/python-variables",
        points_required=5,
        points_reward=15
    )
    
    # Python Course Quiz
    python_quiz = Quiz.objects.create(
        course=python_course,
        lesson=python_lesson1,
        title="Python Basics Quiz",
        description="Test your understanding of Python basics",
        difficulty="EASY",
        time_limit=600,  # 10 minutes
        points_reward=20,
        passing_score=70
    )
    
    # Python Quiz Questions
    q1 = Question.objects.create(
        quiz=python_quiz,
        text="What is the correct way to declare a variable in Python?",
        points=5
    )
    Answer.objects.create(question=q1, text="var x = 5", is_correct=False)
    Answer.objects.create(question=q1, text="x = 5", is_correct=True)
    Answer.objects.create(question=q1, text="dim x = 5", is_correct=False)
    
    q2 = Question.objects.create(
        quiz=python_quiz,
        text="Which of these is a valid Python comment?",
        points=5
    )
    Answer.objects.create(question=q2, text="// This is a comment", is_correct=False)
    Answer.objects.create(question=q2, text="# This is a comment", is_correct=True)
    Answer.objects.create(question=q2, text="/* This is a comment */", is_correct=False)

    # Leadership Course (SOFT skill)
    leadership_course = Course.objects.create(
        title="Effective Leadership",
        description="Develop essential leadership skills for the modern workplace",
        course_type="SOFT",
        points_required=0,
        category="Management",
        tags="leadership,management,soft-skills",
        difficulty_level="INTERMEDIATE",
        estimated_duration=240  # 4 hours
    )
    
    # Leadership Course Lessons
    leadership_lesson1 = Lesson.objects.create(
        course=leadership_course,
        title="Understanding Leadership Styles",
        video_url="https://example.com/leadership-styles",
        points_required=0,
        points_reward=15
    )
    
    leadership_lesson2 = Lesson.objects.create(
        course=leadership_course,
        title="Effective Communication",
        video_url="https://example.com/leadership-communication",
        points_required=0,
        points_reward=15
    )
    
    # Leadership Quiz
    leadership_quiz = Quiz.objects.create(
        course=leadership_course,
        lesson=leadership_lesson1,
        title="Leadership Styles Assessment",
        description="Evaluate your understanding of different leadership styles",
        difficulty="MEDIUM",
        time_limit=900,  # 15 minutes
        points_reward=25,
        passing_score=75
    )
    
    # Leadership Quiz Questions
    q3 = Question.objects.create(
        quiz=leadership_quiz,
        text="Which leadership style involves making decisions without consulting team members?",
        points=5
    )
    Answer.objects.create(question=q3, text="Democratic", is_correct=False)
    Answer.objects.create(question=q3, text="Autocratic", is_correct=True)
    Answer.objects.create(question=q3, text="Laissez-faire", is_correct=False)
    
    # Web Development Course (HARD skill)
    web_course = Course.objects.create(
        title="Full Stack Web Development",
        description="Master both frontend and backend web development",
        course_type="HARD",
        points_required=75,
        category="Web Development",
        tags="javascript,html,css,react,nodejs",
        difficulty_level="ADVANCED",
        estimated_duration=480  # 8 hours
    )
    
    # Web Development Lessons
    web_lesson1 = Lesson.objects.create(
        course=web_course,
        title="HTML & CSS Fundamentals",
        video_url="https://example.com/web-html-css",
        points_required=10,
        points_reward=20
    )
    
    web_lesson2 = Lesson.objects.create(
        course=web_course,
        title="JavaScript Basics",
        video_url="https://example.com/web-javascript",
        points_required=15,
        points_reward=25
    )
    
    # Web Development Quiz
    web_quiz = Quiz.objects.create(
        course=web_course,
        lesson=web_lesson1,
        title="HTML & CSS Quiz",
        description="Test your knowledge of HTML and CSS",
        difficulty="MEDIUM",
        time_limit=1200,  # 20 minutes
        points_reward=30,
        passing_score=80
    )
    
    # Web Quiz Questions
    q4 = Question.objects.create(
        quiz=web_quiz,
        text="Which HTML tag is used to create a hyperlink?",
        points=5
    )
    Answer.objects.create(question=q4, text="<link>", is_correct=False)
    Answer.objects.create(question=q4, text="<a>", is_correct=True)
    Answer.objects.create(question=q4, text="<href>", is_correct=False)
    
    return {
        'python_course': python_course,
        'leadership_course': leadership_course,
        'web_course': web_course
    }

# For testing purposes
@pytest.fixture
def sample_courses():
    return create_sample_courses()

@pytest.mark.django_db
def test_course_creation(sample_courses):
    """Test that courses were created successfully"""
    python_course = sample_courses['python_course']
    leadership_course = sample_courses['leadership_course']
    web_course = sample_courses['web_course']
    
    # Test Python course
    assert python_course.lessons.count() == 2
    assert python_course.quizzes.count() == 1
    assert python_course.course_type == "HARD"
    
    # Test Leadership course
    assert leadership_course.lessons.count() == 2
    assert leadership_course.quizzes.count() == 1
    assert leadership_course.course_type == "SOFT"
    
    # Test Web Development course
    assert web_course.lessons.count() == 2
    assert web_course.quizzes.count() == 1
    assert web_course.course_type == "HARD"
