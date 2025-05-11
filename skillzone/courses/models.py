from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Course(models.Model):
    COURSE_TYPES = [
        ('SOFT', 'Soft Skill'),
        ('HARD', 'Hard Skill'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]
    
    # Fields to match frontend structure
    title = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.FloatField(default=0.0)
    duration = models.IntegerField(default=0)  # Duration in minutes
    course_type = models.CharField(max_length=10, choices=COURSE_TYPES)
    points_reward = models.IntegerField(default=0)  # Points reward for completing the course
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Only for HARD skills
    
    # Additional fields for backend functionality
    difficulty_level = models.CharField(max_length=15, choices=DIFFICULTY_LEVELS, default='BEGINNER')
    category = models.CharField(max_length=100, default='General')
    tags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    external_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    
    def __str__(self):
        return self.title
    
    @property
    def type(self):
        """Return 'soft' or 'hard' to match frontend format"""
        return self.course_type.lower()
    
    @property
    def points(self):
        """Return points_reward to maintain compatibility with frontend"""
        return self.points_reward
    
    @property
    def lessons_count(self):
        return self.lessons.count()

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    number = models.IntegerField()  # Order within the course
    duration = models.IntegerField(default=0)  # Duration in minutes
    video_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for backend functionality
    content = models.TextField(blank=True)
    
    class Meta:
        ordering = ['number']
        unique_together = ['course', 'number']
    
    def __str__(self):
        return f"{self.course.title} - Lesson {self.number}: {self.title}"
    
    @property
    def id(self):
        """Generate ID in the format expected by frontend (e.g., 's1l1')"""
        course_prefix = 's' if self.course.course_type == 'SOFT' else 'h'
        course_id = self.course.id
        return f"{course_prefix}{course_id}l{self.number}"

class UserCourseProgress(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='user_course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
    completed_lessons = models.ManyToManyField(Lesson, related_name='completed_by')
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'course')
        verbose_name = 'User Course Progress'
        verbose_name_plural = 'User Course Progress'
    
    @property
    def progress_percentage(self):
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed_count = self.completed_lessons.count()
        return int((completed_count / total_lessons) * 100)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.course.title}"

class UnlockedCourse(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='unlocked_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='unlocked_by')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'course')
        verbose_name = 'Unlocked Course'
        verbose_name_plural = 'Unlocked Courses'
    
    def __str__(self):
        return f"{self.user.user.username} - {self.course.title}"

class UnlockedLesson(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE, related_name='unlocked_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='unlocked_by')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name = 'Unlocked Lesson'
        verbose_name_plural = 'Unlocked Lessons'
    
    def __str__(self):
        return f"{self.user.user.username} - {self.lesson.title}"
