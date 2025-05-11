from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('quizzes', '0002_alter_quizattempt_user'),
        ('users', '0010_profile_is_teacher'),  # Use the latest applied migration from users
    ]

    operations = [
        # No operations needed, this is just to fix dependencies
    ]