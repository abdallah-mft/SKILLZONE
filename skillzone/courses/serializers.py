from rest_framework import serializers
from .models import Course, Lesson, UnlockedCourse, CourseProgress

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'video_url', 'points_required', 'points_reward')

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    can_access = serializers.SerializerMethodField()
    prerequisites_met = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'course_type', 'points_required',
                 'can_access', 'prerequisites_met', 'progress', 'category',
                 'tags_list', 'difficulty_level', 'estimated_duration', 'lessons')

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

    def get_prerequisites_met(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
            
        user_profile = request.user.profile
        for prerequisite in obj.prerequisites.all():
            progress = CourseProgress.objects.filter(
                user=user_profile,
                course=prerequisite,
                is_completed=True
            ).exists()
            if not progress:
                return False
        return True

    def get_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        progress, created = CourseProgress.objects.get_or_create(
            user=request.user.profile,
            course=obj
        )
        return {
            'percentage': progress.completion_percentage,
            'completed': progress.is_completed,
            'last_activity': progress.last_activity,
            'completed_lessons': list(progress.completed_lessons.values_list('id', flat=True)),
            'completed_quizzes': list(progress.completed_quizzes.values_list('id', flat=True))
        }

    def get_tags_list(self, obj):
        return [tag.strip() for tag in obj.tags.split(',')] if obj.tags else []
