from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Profile
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()

class Command(BaseCommand):
    help = 'Cleans all users from the database except superusers'

    def handle(self, *args, **kwargs):
        try:
            # Get non-superuser users
            users_to_delete = User.objects.filter(is_superuser=False)
            
            # Delete related tokens first
            OutstandingToken.objects.filter(user__in=users_to_delete).delete()
            
            # Delete profiles (due to OneToOne relationship)
            Profile.objects.filter(user__in=users_to_delete).delete()
            
            # Finally delete users
            count = users_to_delete.delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {count} users and their related data')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error while cleaning users: {str(e)}')
            )
