from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'video_url', 'points_required', 'points_reward')

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'course_type', 'lessons')
