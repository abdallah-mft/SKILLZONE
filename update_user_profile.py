# Run this in Django shell (python manage.py shell)
from django.contrib.auth.models import User
from users.models import Profile

# Replace with your actual username
username = 'your_username'  
user = User.objects.get(username=username)

# Create profile if it doesn't exist
if not hasattr(user, 'profile'):
    profile = Profile.objects.create(user=user)
    print("Created new profile")
else:
    profile = user.profile
    print("Using existing profile")

# Set is_teacher to True
profile.is_teacher = True
profile.save()
print(f"Updated profile: is_teacher = {profile.is_teacher}")