# Generated by Django 4.2.7 on 2024-09-06 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0006_user_role_mapping'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='user_role_mapping',
            new_name='user_role_map',
        ),
        migrations.AlterModelTable(
            name='user_role_map',
            table='user_role_map',
        ),
    ]
