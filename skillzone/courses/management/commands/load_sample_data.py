from django.core.management.base import BaseCommand
from courses.tests import create_sample_courses

class Command(BaseCommand):
    help = 'Loads sample courses, lessons, and quizzes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample courses...')
        courses = create_sample_courses()
        self.stdout.write(self.style.SUCCESS('Successfully created sample courses'))
        self.stdout.write(f'Created {len(courses)} courses with lessons and quizzes')
