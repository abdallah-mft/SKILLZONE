from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'Sets default points required for HARD courses'

    def handle(self, *args, **kwargs):
        updated = Course.objects.filter(
            course_type='HARD',
            points_required=0
        ).update(points_required=1000)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated} HARD courses')
        )