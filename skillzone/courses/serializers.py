from rest_framework import serializers
from .models import Course, Lesson, UnlockedCourse

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'video_url', 'points_required', 'points_reward')

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'course_type', 'points_required', 
                 'is_available', 'is_unlocked', 'lessons')

    def get_is_available(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # For SOFT courses, always available
            if obj.course_type == 'SOFT':
                return True
            # For HARD courses, check if unlocked
            return UnlockedCourse.objects.filter(
                user=request.user.profile,
                course=obj
            ).exists()
        return False

    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UnlockedCourse.objects.filter(
                user=request.user.profile,
                course=obj
            ).exists()
        return False
