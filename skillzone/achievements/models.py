from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

class Achievement(models.Model):
    TYPES = (
        ('BADGE', 'Badge'),
        ('CERTIFICATE', 'Certificate'),
        ('MILESTONE', 'Milestone'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES)
    icon = models.ImageField(upload_to='achievements/icons/')
    points_reward = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    requirements = models.JSONField(
        help_text="Criteria to unlock achievement"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"

class UserAchievement(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    progress = models.JSONField(
        default=dict,
        help_text="Progress towards achievement"
    )

    class Meta:
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"