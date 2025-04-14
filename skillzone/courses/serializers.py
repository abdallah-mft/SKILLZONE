from rest_framework import serializers
from .models import Course, Lesson, UnlockedCourse, UnlockedLesson

class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'video_url', 'points_required', 'is_completed', 'completed_at')

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UnlockedLesson.objects.filter(
                user=request.user.profile,
                lesson=obj,
                completed_at__isnull=False
            ).exists()
        return False

    def get_completed_at(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            unlocked_lesson = UnlockedLesson.objects.filter(
                user=request.user.profile,
                lesson=obj,
                completed_at__isnull=False
            ).first()
            return unlocked_lesson.completed_at if unlocked_lesson else None
        return None

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    can_access = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    completion_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'course_type', 
                 'points_required', 'can_access', 'category',
                 'tags_list', 'difficulty_level', 'estimated_duration', 
                 'lessons', 'completion_stats')

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

    def get_completion_stats(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            total_lessons = obj.lessons.count()
            completed_lessons = UnlockedLesson.objects.filter(
                user=request.user.profile,
                lesson__course=obj,
                completed_at__isnull=False
            ).count()
            return {
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'completion_percentage': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            }
        return None
