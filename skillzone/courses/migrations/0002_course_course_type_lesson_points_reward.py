# Generated by Django 5.1.6 on 2025-03-07 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_type',
            field=models.CharField(choices=[('SOFT', 'Soft Skills'), ('HARD', 'Hard Skills')], default='HARD', max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lesson',
            name='points_reward',
            field=models.IntegerField(default=0),
        ),
    ]
