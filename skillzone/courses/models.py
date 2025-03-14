from django.db import models
from django.core.exceptions import ValidationError

class Course(models.Model):
    COURSE_TYPES = (
        ('SOFT', 'Soft Skills'),
        ('HARD', 'Hard Skills'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_type = models.CharField(max_length=4, choices=COURSE_TYPES)
    points_required = models.IntegerField(default=0)

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

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    points_required = models.IntegerField(default=0)
    points_reward = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class UnlockedLesson(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

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
