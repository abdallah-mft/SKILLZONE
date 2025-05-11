# Rename this file to a proper migration number
# For example, rename to 0016_squashed_migrations.py

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
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verification_code', models.CharField(blank=True, max_length=4)),
                ('email_verified', models.BooleanField(default=False)),
                ('code_created_at', models.DateTimeField(null=True)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('notification_preferences', models.JSONField(default=dict)),
                ('points', models.IntegerField(default=0)),
                ('is_teacher', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user',), name='unique_user_profile')],
            },
        ),
    ]
