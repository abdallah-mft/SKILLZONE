from rest_framework import serializers
from .models import Course, Lesson, UnlockedCourse

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'video_url', 'points_required')

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    can_access = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'course_type', 
                 'points_required', 'can_access', 'category',
                 'tags_list', 'difficulty_level', 'estimated_duration', 
                 'lessons')

    def get_can_access(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # SOFT courses are always accessible
            if obj.course_type == 'SOFT':
                return True
            
            # For HARD courses, check if unlocked
            return UnlockedCourse.objects.filter(
                user=request.user.profile,
                course=obj
            ).exists()
        return False

    def get_tags_list(self, obj):
        return [tag.strip() for tag in obj.tags.split(',')] if obj.tags else []
