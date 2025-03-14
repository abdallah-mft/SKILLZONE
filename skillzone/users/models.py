from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    device_token = models.CharField(max_length=255, blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)

    def get_level(self):
        return Level.objects.filter(
            min_points__lte=self.points,
            max_points__gte=self.points
        ).first()

    def __str__(self):
        return self.user.username

class Level(models.Model):
    LEVEL_CHOICES = [
        ('ROOKIE', 'Rookie'),        # 0-99 points
        ('EXPLORER', 'Explorer'),    # 100-299 points
        ('ACHIEVER', 'Achiever'),    # 300-499 points
        ('MASTER', 'Master'),        # 500-799 points
        ('GRANDMASTER', 'Grandmaster')  # 800+ points
    ]

    name = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    min_points = models.IntegerField()
    max_points = models.IntegerField()
    badge_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
