# Generated by Django 4.2.7 on 2024-12-02 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0010_alter_password_storage_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_role_map',
            name='site_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
