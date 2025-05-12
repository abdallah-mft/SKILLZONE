# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', 'fix_usercourseprogress_fk'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Copy data from points_reward to points (if needed) and drop points_reward
            sql="""
            -- First, update points with points_reward values where points is 0 or NULL
            UPDATE courses_course 
            SET points = points_reward 
            WHERE (points IS NULL OR points = 0) AND points_reward > 0;
            
            -- Then drop the points_reward column
            ALTER TABLE courses_course DROP COLUMN points_reward;
            """,
            
            # Reverse SQL - If you need to roll back (recreate points_reward)
            reverse_sql="""
            ALTER TABLE courses_course ADD COLUMN points_reward integer;
            UPDATE courses_course SET points_reward = points;
            """
        ),
    ]