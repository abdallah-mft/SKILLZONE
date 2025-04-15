from django.core.management.base import BaseCommand
from courses.models import Course

class Command(BaseCommand):
    help = 'Fixes lesson numbers for all courses to ensure sequential ordering'

    def handle(self, *args, **kwargs):
        courses = Course.objects.all()
        total_updated = 0

        for course in courses:
            lessons = course.lessons.all().order_by('id')
            for index, lesson in enumerate(lessons, start=1):
                if lesson.number != index:
                    lesson.number = index
                    lesson.save()
                    total_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {total_updated} lesson numbers across {courses.count()} courses'
            )
        )


