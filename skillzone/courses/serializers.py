from rest_framework import serializers
from .models import Course, Lesson, UserCourseProgress

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'number', 'duration', 'video_url']

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    # Add this line to create a virtual 'points' field that maps to points_reward
    points = serializers.IntegerField(source='points_reward', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'rating', 'duration', 
            'course_type', 'points', 'points_reward', 'price', 'difficulty_level', 
            'category', 'tags', 'lessons', 'lessons_count'
        ]

class UserCourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    completed_lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserCourseProgress
        fields = [
            'id', 'user', 'course', 'completed_lessons', 
            'is_completed', 'started_at', 'completed_at', 'progress_percentage'
        ]
