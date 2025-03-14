from django.db import migrations, models

def create_levels(apps, schema_editor):
    Level = apps.get_model('users', 'Level')
    levels = [
        {'name': 'ROOKIE', 'min_points': 0, 'max_points': 99},
        {'name': 'EXPLORER', 'min_points': 100, 'max_points': 299},
        {'name': 'ACHIEVER', 'min_points': 300, 'max_points': 499},
        {'name': 'MASTER', 'min_points': 500, 'max_points': 799},
        {'name': 'GRANDMASTER', 'min_points': 800, 'max_points': 999999},
    ]
    
    for level in levels:
        Level.objects.create(**level)

def reverse_levels(apps, schema_editor):
    Level = apps.get_model('users', 'Level')
    Level.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('ROOKIE', 'Rookie'), ('EXPLORER', 'Explorer'), ('ACHIEVER', 'Achiever'), ('MASTER', 'Master'), ('GRANDMASTER', 'Grandmaster')], max_length=20)),
                ('min_points', models.IntegerField()),
                ('max_points', models.IntegerField()),
                ('badge_url', models.URLField(blank=True)),
            ],
        ),
        migrations.RunPython(create_levels, reverse_levels),
    ]