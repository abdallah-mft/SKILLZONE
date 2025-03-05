from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    points_required = models.IntegerField(default=0)  # Points required to unlock (0 = free)

    def __str__(self):
        return self.title
