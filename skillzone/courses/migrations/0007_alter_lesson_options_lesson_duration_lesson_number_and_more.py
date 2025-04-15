from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_remove_course_estimated_duration_course_duration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='duration',
            field=models.IntegerField(default=0, help_text='Duration in minutes', validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddField(
            model_name='lesson',
            name='number',
            field=models.IntegerField(default=1, help_text='Lesson number/order within the course'),
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['number']},
        ),
    ]
