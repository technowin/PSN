# Generated by Django 4.2.7 on 2024-08-28 08:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0006_rename_checksum_description_file_checksum_checksum_message_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file_checksum',
            name='date',
        ),
    ]