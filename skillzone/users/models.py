from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    device_token = models.CharField(max_length=255, blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
