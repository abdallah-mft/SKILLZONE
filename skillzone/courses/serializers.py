from rest_framework import serializers
from .models import Course, Lesson, UserCourseProgress, UnlockedCourse

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'number', 'duration', 'video_url']

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'category', 'difficulty_level', 
                  'course_type', 'points_reward', 'points_required', 'lessons_count', 
                  'is_unlocked', 'progress', 'created_at', 'updated_at']
    
    def get_lessons_count(self, obj):
        return obj.lessons.count()
    
    def get_is_unlocked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        return UnlockedCourse.objects.filter(
            user=request.user.profile,
            course=obj
        ).exists()
    
    def get_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progress = UserCourseProgress.objects.get(
                user=request.user.profile,
                course=obj
            )
            
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return 0
                
            completed_lessons = progress.completed_lessons.count()
            return {
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'percentage': int((completed_lessons / total_lessons) * 100),
                'is_completed': progress.is_completed
            }
        except UserCourseProgress.DoesNotExist:
            return None

class UserCourseProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    completed_lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserCourseProgress
        fields = [
            'id', 'user', 'course', 'completed_lessons', 
            'is_completed', 'started_at', 'completed_at', 'progress_percentage'
        ]
