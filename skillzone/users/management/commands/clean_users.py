from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Cleans all users from the database except superusers'

    def handle(self, *args, **kwargs):
        # Delete all profiles first (due to OneToOne relationship)
        Profile.objects.all().delete()
        
        # Delete all non-superuser users
        users_deleted = User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {users_deleted[0]} users')
        )