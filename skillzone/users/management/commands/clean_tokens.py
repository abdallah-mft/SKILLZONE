from django.core.management.base import BaseCommand
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

class Command(BaseCommand):
    help = 'Cleans all tokens from the database'

    def handle(self, *args, **kwargs):
        try:
            # Delete all tokens
            outstanding_count = OutstandingToken.objects.all().delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {outstanding_count} tokens')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error while cleaning tokens: {str(e)}')
            )