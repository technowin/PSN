# Generated by Django 4.2.7 on 2024-08-16 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0012_alter_site_master_roster_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='sc_employee_master',
            name='is_active',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]