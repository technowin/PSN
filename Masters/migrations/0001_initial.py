# Generated by Django 4.2.7 on 2024-08-23 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='company_master',
            fields=[
                ('company_id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.TextField(blank=True, null=True)),
                ('company_address', models.TextField(blank=True, null=True)),
                ('pincode', models.TextField(blank=True, null=True)),
                ('contact_person_name', models.TextField(blank=True, null=True)),
                ('contact_person_email', models.TextField(blank=True, null=True)),
                ('contact_person_mobile_no', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'company_master',
            },
        ),
        migrations.CreateModel(
            name='file_checksum',
            fields=[
                ('checksum_id', models.AutoField(primary_key=True, serialize=False)),
                ('upload_for', models.TextField(blank=True, null=True)),
                ('site', models.TextField(blank=True, null=True)),
                ('month', models.TextField(blank=True, null=True)),
                ('year', models.TextField(blank=True, null=True)),
                ('file_name', models.TextField(blank=True, null=True)),
                ('checksum_description', models.TextField(blank=True, null=True)),
                ('uploaded_date', models.DateTimeField(blank=True, null=True)),
                ('operation_type', models.TextField(blank=True, null=True)),
                ('status', models.TextField(blank=True, null=True)),
                ('error_count', models.TextField(blank=True, null=True)),
                ('update_count', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checksum_company', to='Masters.company_master')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checksum_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checksum_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'file_checksum',
            },
        ),
        migrations.CreateModel(
            name='parameter_master',
            fields=[
                ('parameter_id', models.AutoField(primary_key=True, serialize=False)),
                ('parameter_name', models.TextField(blank=True, null=True)),
                ('parameter_value', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'parameter_master',
            },
        ),
        migrations.CreateModel(
            name='site_master',
            fields=[
                ('site_id', models.AutoField(primary_key=True, serialize=False)),
                ('site_name', models.TextField(blank=True, null=True)),
                ('site_address', models.TextField(blank=True, null=True)),
                ('pincode', models.TextField(blank=True, null=True)),
                ('contact_person_name', models.TextField(blank=True, null=True)),
                ('contact_person_email', models.TextField(blank=True, null=True)),
                ('contact_person_mobile_no', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('roster_type', models.TextField(blank=True, null=True)),
                ('no_of_days', models.BigIntegerField(null=True)),
                ('notification_time', models.TimeField(blank=True, null=True)),
                ('reminder_time', models.TimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_relation', to='Masters.company_master')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='site_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='site_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'site_master',
            },
        ),
        migrations.CreateModel(
            name='sc_roster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_id', models.TextField(blank=True, null=True)),
                ('site', models.TextField(blank=True, null=True)),
                ('shift_date', models.DateField(blank=True, null=True)),
                ('shift_time', models.TextField(blank=True, null=True)),
                ('confirmation', models.BooleanField(blank=True, default=False, null=True)),
                ('attendance', models.TextField(blank=True, null=True)),
                ('uploaded_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roster_company', to='Masters.company_master')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roster_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roster_updated_by', to=settings.AUTH_USER_MODEL)),
                ('uploaded_by', models.ForeignKey(blank=True, db_column='uploaded_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sc_roster',
            },
        ),
        migrations.CreateModel(
            name='sc_employee_master',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_id', models.TextField(blank=True, null=True)),
                ('employee_name', models.TextField(blank=True, null=True)),
                ('mobile_no', models.TextField(blank=True, null=True)),
                ('current_location', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sc_employee_created', to=settings.AUTH_USER_MODEL)),
                ('employment_status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parameter_data', to='Masters.parameter_master')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sc_employee_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sc_employee_master',
            },
        ),
        migrations.CreateModel(
            name='Roles',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role_id', models.IntegerField(null=True)),
                ('role_name', models.TextField(blank=True, null=True)),
                ('role_type', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'roles',
            },
        ),
        migrations.CreateModel(
            name='file_errorlog',
            fields=[
                ('error_id', models.AutoField(primary_key=True, serialize=False)),
                ('upload_for', models.TextField(blank=True, null=True)),
                ('site', models.TextField(blank=True, null=True)),
                ('month', models.TextField(blank=True, null=True)),
                ('year', models.TextField(blank=True, null=True)),
                ('file_name', models.TextField(blank=True, null=True)),
                ('error_description', models.TextField(blank=True, null=True)),
                ('uploaded_date', models.DateTimeField(blank=True, null=True)),
                ('operation_type', models.TextField(blank=True, null=True)),
                ('status', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('checksum', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checksum1_created_by', to='Masters.file_checksum')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='errorlog_company', to='Masters.company_master')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='file_errorlog_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='file_errorlog_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'file_errorlog',
            },
        ),
        migrations.CreateModel(
            name='application_search',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('href', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_search_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_search_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'application_search',
            },
        ),
    ]
