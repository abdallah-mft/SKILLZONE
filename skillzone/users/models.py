from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    device_token = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_preferences = models.JSONField(default=dict)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['points']),
        ]

    def get_level(self):
        """Get user's current level based on points"""
        return Level.objects.filter(
            min_points__lte=self.points,
            max_points__gte=self.points
        ).first()

    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])

    def __str__(self):
        return f"{self.user.username}'s profile"

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
