# Generated by Django 4.2.7 on 2024-08-16 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0011_application_search'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site_master',
            name='roster_type',
            field=models.TextField(blank=True, null=True),
        ),
    ]