# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_course_image_alter_unlockedcourse_unlocked_at'),
        ('users', '0017_level'),  # Make sure this is the latest users migration
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Drop the old constraint and create a new one
            sql="""
            ALTER TABLE courses_usercourseprogress 
            DROP CONSTRAINT courses_usercourseprogress_user_id_16683a45_fk_auth_user_id;
            
            ALTER TABLE courses_usercourseprogress
            ADD CONSTRAINT courses_usercourseprogress_user_id_fk_users_profile
            FOREIGN KEY (user_id) REFERENCES users_profile(id)
            ON DELETE CASCADE;
            """,
            
            # Reverse SQL - If you need to roll back
            reverse_sql="""
            ALTER TABLE courses_usercourseprogress 
            DROP CONSTRAINT courses_usercourseprogress_user_id_fk_users_profile;
            
            ALTER TABLE courses_usercourseprogress
            ADD CONSTRAINT courses_usercourseprogress_user_id_16683a45_fk_auth_user_id
            FOREIGN KEY (user_id) REFERENCES auth_user(id)
            ON DELETE CASCADE;
            """
        ),
    ]