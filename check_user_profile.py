# Run this in Django shell (python manage.py shell)
from django.contrib.auth.models import User
from users.models import Profile

# Replace with your actual username
username = 'your_username'  
user = User.objects.get(username=username)

# Check if profile exists
if hasattr(user, 'profile'):
    print(f"Profile exists: {user.profile}")
    print(f"Is teacher: {user.profile.is_teacher}")
else:
    print("Profile doesn't exist")