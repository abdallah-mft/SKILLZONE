from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Course(models.Model):
    COURSE_TYPES = (
        ('SOFT', 'Soft Skills'),
        ('HARD', 'Hard Skills'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    duration = models.IntegerField(
        help_text="Duration in minutes",
        default=0,
        validators=[MinValueValidator(0)]
    )
    course_type = models.CharField(max_length=4, choices=COURSE_TYPES)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    points_required = models.IntegerField(default=0)
    points_reward = models.IntegerField(default=0)
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        null=True,
        blank=True
    )
    
    # Keeping these fields as they seem important for the system
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    category = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('BEGINNER', 'Beginner'),
            ('INTERMEDIATE', 'Intermediate'),
            ('ADVANCED', 'Advanced')
        ],
        default='BEGINNER'
    )

    def clean(self):
        if self.course_type == 'HARD' and self.points_required <= 0:
            raise ValidationError({
                'points_required': 'HARD courses must require points to unlock'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_liked(self):
        # This should be handled in the serializer based on the current user
        return False

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    number = models.IntegerField(
        default=1,
        help_text="Lesson number/order within the course"
    )
    duration = models.IntegerField(
        help_text="Duration in minutes",
        default=0,
        validators=[MinValueValidator(0)]
    )
    video_url = models.URLField()
    points_required = models.IntegerField(default=0)

    class Meta:
        ordering = ['number']  # This will ensure lessons are ordered by their number
        unique_together = ['course', 'number']  # Ensures no duplicate lesson numbers in a course

    def __str__(self):
        return f"{self.course.title} - Lesson {self.number}: {self.title}"

    @property
    def is_completed(self):
        # This will be handled in the serializer based on UnlockedLesson
        return False

class UnlockedLesson(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.user.username} - {self.lesson.title}"

class UnlockedCourse(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    points_spent = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.user.username} - {self.course.title}"

class CourseProgress(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    completed_lessons = models.ManyToManyField(Lesson)
    completed_quizzes = models.ManyToManyField('quizzes.Quiz')
    
    @property
    def completion_percentage(self):
        total_items = self.course.lessons.count() + self.course.quizzes.count()
        completed_items = self.completed_lessons.count() + self.completed_quizzes.count()
        return (completed_items / total_items * 100) if total_items > 0 else 0
    
    @property
    def is_completed(self):
        return self.completion_percentage == 100
    
    class Meta:
        unique_together = ['user', 'course']

class CourseEnrollment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'course']

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
