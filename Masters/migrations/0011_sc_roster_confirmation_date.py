# Generated by Django 4.2.7 on 2024-09-03 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0010_sc_roster_checksum'),
    ]

    operations = [
        migrations.AddField(
            model_name='sc_roster',
            name='confirmation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
