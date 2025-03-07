from django.db import models

class Course(models.Model):
    COURSE_TYPES = (
        ('SOFT', 'Soft Skills'),
        ('HARD', 'Hard Skills'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    course_type = models.CharField(max_length=4, choices=COURSE_TYPES)

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
