from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'Sets default points reward for courses based on difficulty'

    def handle(self, *args, **kwargs):
        # Define points based on difficulty
        rewards = {
            'BEGINNER': 100,
            'INTERMEDIATE': 200,
            'ADVANCED': 300
        }
        
        updated = 0
        for difficulty, points in rewards.items():
            count = Course.objects.filter(
                difficulty_level=difficulty,
                points_reward=0
            ).update(points_reward=points)
            updated += count
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated} courses with reward points')
        )