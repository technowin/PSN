# Generated by Django 4.2.7 on 2024-08-22 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0006_alter_customuser_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='encrypted_password',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='password_text',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='title',
        ),
    ]
