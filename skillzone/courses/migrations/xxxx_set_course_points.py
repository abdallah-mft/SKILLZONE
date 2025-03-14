from django.db import migrations

def set_course_points(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    # Set points for all HARD courses that don't have points set
    Course.objects.filter(course_type='HARD', points_required=0).update(points_required=1000)

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0003_course_points_required'),
    ]

    operations = [
        migrations.RunPython(set_course_points),
    ]