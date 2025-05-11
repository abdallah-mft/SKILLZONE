import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import uuid
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

# First, modify OutstandingToken to cascade delete
OutstandingToken._meta.get_field('user').remote_field.on_delete = models.CASCADE

# Add a pre-delete signal handler for User
@receiver(pre_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Delete all related data before deleting the user
    This ensures proper order of deletion
    """
    # Delete tokens first
    OutstandingToken.objects.filter(user=instance).delete()
    
    # Delete profile (should happen automatically due to CASCADE)
    try:
        instance.profile.delete()
    except:
        pass

    # Add other specific deletions here if needed
    # For example:
    # instance.quizzes.all().delete()
    # instance.course_enrollments.all().delete()
    # etc.

class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    verification_code = models.CharField(max_length=4, blank=True)
    email_verified = models.BooleanField(default=False)
    code_created_at = models.DateTimeField(null=True)
    bio = models.TextField(max_length=500, blank=True)
    notification_preferences = models.JSONField(default=dict)
    points = models.IntegerField(default=0)
    is_teacher = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_profile')
        ]

    def __str__(self):
        return f"{self.user.username}'s profile"

    def generate_verification_code(self):
        """Generate a 4-digit verification code using uppercase letters and numbers"""
        characters = string.ascii_uppercase + string.digits
        self.verification_code = ''.join(random.choices(characters, k=4))
        self.code_created_at = timezone.now()
        self.save()
        return self.verification_code

    def is_verification_code_valid(self, code):
        """Check if verification code is valid and not expired"""
        if not self.code_created_at:
            return False
        
        # Check if code is expired (valid for 1 hour)
        time_diff = timezone.now() - self.code_created_at
        if time_diff.total_seconds() > 3600:  # 1 hour in seconds
            return False
            
        return self.verification_code == code.upper()

    def verify_email(self):
        """Mark email as verified and clear verification code"""
        self.email_verified = True
        self.verification_code = ''
        self.code_created_at = None
        self.save()

    def add_points(self, points_to_add):
        """Safely add points with validation"""
        if points_to_add < 0:
            raise ValueError("Cannot add negative points")
        self.points += points_to_add
        self.save()
        return self.points

    def deduct_points(self, points_to_deduct):
        """Safely deduct points with validation"""
        if points_to_deduct < 0:
            raise ValueError("Cannot deduct negative points")
        if self.points < points_to_deduct:
            raise ValueError("Insufficient points")
        self.points -= points_to_deduct
        self.save()
        return self.points

    def get_level(self):
        """Calculate user level based on points"""
        levels = [
            (0, 1),      # 0-99 points = Level 1
            (100, 2),    # 100-299 points = Level 2
            (300, 3),    # 300-599 points = Level 3
            (600, 4),    # 600-999 points = Level 4
            (1000, 5),   # 1000+ points = Level 5
        ]
        for threshold, level in levels:
            if self.points < threshold:
                return level - 1
        return len(levels)

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
