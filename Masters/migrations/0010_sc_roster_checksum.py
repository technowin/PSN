# Generated by Django 4.2.7 on 2024-08-28 10:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0009_remove_file_errorlog_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='sc_roster',
            name='checksum',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checksum_roster', to='Masters.file_checksum'),
        ),
    ]
