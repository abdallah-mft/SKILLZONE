# Renamed from squashed_migrations.py to 0016_squashed_migrations.py

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    # Keep the replaces attribute to indicate this is a squashed migration
    replaces = [
        ('users', '0001_initial'),
        ('users', '0002_remove_profile_users_profi_user_id_783607_idx_and_more'),
        ('users', '0003_remove_profile_email_verification_token_and_more'),
        ('users', '0004_remove_profile_email_verified_and_more'),
        ('users', '0005_profile_email_verified'),
        ('users', '0006_profile_bio_profile_notification_preferences'),
        ('users', '0007_profile_points'),
        ('users', '0008_remove_profile_verification_token_and_more'),
        ('users', '0009_alter_profile_user'),
        ('users', '0010_profile_is_teacher'),
        ('users', '0011_profile_user_type'),
        ('users', '0012_remove_profile_is_teacher'),
        ('users', '0013_remove_profile_user_type'),
        ('users', '0014_profile_is_teacher'),
        ('users', '0015_acknowledge_is_teacher'),
    ]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Keep your operations as they are
    ]