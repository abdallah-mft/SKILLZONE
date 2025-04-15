from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError

User = get_user_model()

def validate_file_size(value):
    limit = 2 * 1024 * 1024  # 2 MB
    if value.size > limit:
        raise ValidationError(f'File size cannot be larger than 2 MB')

def validate_achievement_requirements(value):
    if not isinstance(value, dict):
        raise ValidationError('Requirements must be a dictionary')
    if not value:
        raise ValidationError('Requirements cannot be empty')
    for key, requirement in value.items():
        if not isinstance(key, str):
            raise ValidationError('Requirement keys must be strings')
        if not isinstance(requirement, dict):
            raise ValidationError('Each requirement must be a dictionary')
        if 'type' not in requirement:
            raise ValidationError('Each requirement must have a "type" field')
        if 'value' not in requirement:
            raise ValidationError('Each requirement must have a "value" field')
        if not isinstance(requirement['value'], (int, float, str, bool)):
            raise ValidationError('Requirement value must be a valid type (int, float, str, bool)')

class Achievement(models.Model):
    TYPES = (
        ('BADGE', 'Badge'),
        ('CERTIFICATE', 'Certificate'),
        ('MILESTONE', 'Milestone'),
        ('STREAK', 'Learning Streak'),
        ('SOCIAL', 'Social Achievement')
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES)
    icon = models.ImageField(
        upload_to='achievements/icons/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ]
    )
    points_reward = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    requirements = models.JSONField(
        help_text="Criteria to unlock achievement",
        validators=[validate_achievement_requirements]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-points_reward', 'title']
        indexes = [
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['points_reward']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

    def clean(self):
        if not self.requirements:
            raise ValidationError({'requirements': 'Requirements cannot be empty'})
        validate_achievement_requirements(self.requirements)

class UserAchievement(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
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
