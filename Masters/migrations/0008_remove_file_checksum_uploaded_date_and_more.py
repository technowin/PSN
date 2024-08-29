# Generated by Django 4.2.7 on 2024-08-28 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0007_remove_file_checksum_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file_checksum',
            name='uploaded_date',
        ),
        migrations.RemoveField(
            model_name='file_errorlog',
            name='uploaded_date',
        ),
        migrations.AddField(
            model_name='file_checksum',
            name='month',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='file_checksum',
            name='year',
            field=models.TextField(blank=True, null=True),
        ),
    ]
