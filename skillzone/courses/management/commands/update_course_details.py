from django.core.management.base import BaseCommand
from django.utils import timezone
from courses.models import Course, Lesson
from datetime import timedelta

class Command(BaseCommand):
    help = 'Updates all courses with complete details and validates data'

    def handle(self, *args, **kwargs):
        # Default values for different difficulty levels
        difficulty_rewards = {
            'BEGINNER': 100,
            'INTERMEDIATE': 200,
            'ADVANCED': 300
        }

        # Update all courses
        courses = Course.objects.all()
        updated_count = 0

        for course in courses:
            modified = False

            # Ensure points_required for HARD courses
            if course.course_type == 'HARD' and course.points_required <= 0:
                course.points_required = 1000
                modified = True

            # Ensure points_reward based on difficulty
            if course.points_reward <= 0:
                course.points_reward = difficulty_rewards.get(course.difficulty_level, 100)
                modified = True

            # Ensure estimated_duration
            if course.estimated_duration <= 0:
                # Calculate based on number of lessons (15 mins per lesson)
                lesson_count = course.lessons.count()
                course.estimated_duration = lesson_count * 15 if lesson_count > 0 else 30
                modified = True

            # Ensure category
            if not course.category:
                course.category = 'General'
                modified = True

            # Ensure tags
            if not course.tags:
                course.tags = f"{course.course_type},{course.difficulty_level}"
                modified = True

            if modified:
                try:
                    course.full_clean()
                    course.save()
                    updated_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating course {course.id}: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} courses')
        )

        # Verify all lessons have required fields
        lessons = Lesson.objects.all()
        lesson_count = 0

        for lesson in lessons:
            modified = False

            # Ensure video_url
            if not lesson.video_url:
                lesson.video_url = f"https://example.com/videos/lesson-{lesson.id}"
                modified = True

            # Set points_required based on course type
            if lesson.points_required <= 0:
                if lesson.course.course_type == 'HARD':
                    lesson.points_required = 50
                else:
                    lesson.points_required = 0
                modified = True

            if modified:
                try:
                    lesson.save()
                    lesson_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error updating lesson {lesson.id}: {str(e)}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {lesson_count} lessons')
        )