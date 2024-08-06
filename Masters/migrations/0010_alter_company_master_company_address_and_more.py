# Generated by Django 4.2.7 on 2024-08-06 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0009_alter_company_master_company_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company_master',
            name='company_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company_master',
            name='company_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company_master',
            name='contact_person_email',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company_master',
            name='contact_person_mobile_no',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company_master',
            name='contact_person_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='company_master',
            name='pincode',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parameter_master',
            name='parameter_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='parameter_master',
            name='parameter_value',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sc_employee_master',
            name='current_location',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sc_employee_master',
            name='employee_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sc_employee_master',
            name='employee_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sc_employee_master',
            name='employee_status',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sc_employee_master',
            name='mobile_no',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sc_roaster',
            name='employee_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='site_master',
            name='contact_person_email',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='site_master',
            name='contact_person_mobile_no',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='site_master',
            name='contact_person_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='site_master',
            name='pincode',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='site_master',
            name='site_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='site_master',
            name='site_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
