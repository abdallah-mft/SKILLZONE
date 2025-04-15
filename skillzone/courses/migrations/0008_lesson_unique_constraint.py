from django.db import migrations

def fix_lesson_numbers(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for course in Course.objects.all():
        lessons = course.lessons.all().order_by('id')
        for index, lesson in enumerate(lessons, start=1):
            lesson.number = index
            lesson.save()

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_lesson_options_lesson_duration_lesson_number_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_lesson_numbers),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('course', 'number')},
        ),
    ]