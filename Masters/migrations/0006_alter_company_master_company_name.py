# Generated by Django 4.2.7 on 2024-08-06 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0005_alter_company_master_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company_master',
            name='company_name',
            field=models.TextField(max_length=800),
        ),
    ]