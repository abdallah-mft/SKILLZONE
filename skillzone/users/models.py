from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verified = models.BooleanField(default=False)
    bio = models.TextField(max_length=500, blank=True)
    notification_preferences = models.JSONField(default=dict)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_profile')
        ]

    def __str__(self):
        return f"{self.user.username}'s profile"

    def generate_verification_token(self):
        self.verification_token = uuid.uuid4()
        self.save()
        return self.verification_token

    def get_level(self):
        """Calculate user level based on points"""
        if self.points < 100:
            return 1
        elif self.points < 300:
            return 2
        elif self.points < 600:
            return 3
        elif self.points < 1000:
            return 4
        else:
            return 5

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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
