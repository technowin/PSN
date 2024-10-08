# Generated by Django 4.2.7 on 2024-08-28 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0005_rename_current_location_sc_employee_master_worksite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file_checksum',
            old_name='checksum_description',
            new_name='checksum_message',
        ),
        migrations.RenameField(
            model_name='file_checksum',
            old_name='month',
            new_name='worksite',
        ),
        migrations.RenameField(
            model_name='file_errorlog',
            old_name='error_description',
            new_name='error_message',
        ),
        migrations.RenameField(
            model_name='file_errorlog',
            old_name='month',
            new_name='worksite',
        ),
        migrations.RemoveField(
            model_name='file_checksum',
            name='operation_type',
        ),
        migrations.RemoveField(
            model_name='file_checksum',
            name='site',
        ),
        migrations.RemoveField(
            model_name='file_checksum',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='file_checksum',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='file_checksum',
            name='year',
        ),
        migrations.RemoveField(
            model_name='file_errorlog',
            name='operation_type',
        ),
        migrations.RemoveField(
            model_name='file_errorlog',
            name='site',
        ),
        migrations.RemoveField(
            model_name='file_errorlog',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='file_errorlog',
            name='updated_by',
        ),
        migrations.RemoveField(
            model_name='file_errorlog',
            name='year',
        ),
        migrations.AddField(
            model_name='file_checksum',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='file_errorlog',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
