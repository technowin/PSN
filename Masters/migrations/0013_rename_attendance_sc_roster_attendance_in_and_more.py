# Generated by Django 4.2.7 on 2024-09-12 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0012_log'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sc_roster',
            old_name='attendance',
            new_name='attendance_in',
        ),
        migrations.AddField(
            model_name='sc_roster',
            name='attendance_out',
            field=models.TextField(blank=True, null=True),
        ),
    ]
