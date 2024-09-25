from django.db import models

# Create your models here.

from django.db import models

from Account.models import CustomUser

     
class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    role_id = models.IntegerField(null=True, blank=False)
    role_name = models.TextField(null=True, blank=True)
    role_type = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey('Account.CustomUser', on_delete=models.CASCADE, related_name='roles_created', blank=True, null=True, db_column='created_by')
    updated_by = models.ForeignKey('Account.CustomUser', on_delete=models.CASCADE, related_name='roles_updated', blank=True, null=True, db_column='updated_by')
    class Meta:
        db_table = 'roles'



# Create your models here.
class company_master(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.TextField(null=True,blank=True)
    company_address =models.TextField(null=True,blank=True)
    pincode =models.TextField(null=True,blank=True)
    contact_person_name =models.TextField(null=True,blank=True)
    contact_person_email =models.TextField(null=True,blank=True)
    contact_person_mobile_no =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='company_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='company_updated_by',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'company_master'
    def __str__(self):
        return self.company_name



class parameter_master(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name =models.TextField(null=True,blank=True)
    parameter_value =models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='parameter_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='parameter_updated_by',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'parameter_master'
    def __str__(self):
        return self.parameter_name

class site_master(models.Model):
    site_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='company_relation',blank=True, null=True)
    site_name =models.TextField(null=True,blank=True)
    site_address =models.TextField(null=True,blank=True)
    pincode =models.TextField(null=True,blank=True)
    contact_person_name =models.TextField(null=True,blank=True)
    contact_person_email =models.TextField(null=True,blank=True)
    contact_person_mobile_no =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    roster_type =models.TextField(null=True,blank=True)
    # roster_type = models.ForeignKey(parameter_master, on_delete=models.CASCADE,related_name='company_relation',blank=True, null=True,db_column='roster_type')
    no_of_days =models.BigIntegerField(null=True,blank=False)
    notification_time=models.TimeField(null=True,blank=True)
    reminder_time = models.TimeField(null=True,blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='site_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='site_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'site_master'
    def __str__(self):
        return self.site_name
    
class sc_employee_master(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id =models.TextField(null=True,blank=True)
    employee_name =models.TextField(null=True,blank=True)
    mobile_no =models.TextField(null=True,blank=True)
    worksite =models.TextField(null=True,blank=True)
    employment_status = models.ForeignKey(parameter_master, on_delete=models.CASCADE,related_name='parameter_data',blank=True, null=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='sc_employee_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='sc_employee_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'sc_employee_master'
    def __str__(self):
        return self.employee_name
    
 
class application_search(models.Model):
    id = models.AutoField(primary_key=True)
    name =models.TextField(null=True,blank=True)
    description =models.TextField(null=True,blank=True)
    href =models.TextField(null=True,blank=True)
    menu_id =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'application_search'
    def __str__(self):
        return self.name

class file_checksum(models.Model):
    checksum_id = models.AutoField(primary_key=True)
    upload_for =models.TextField(null=True,blank=True)
    company = models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='checksum_company',blank=True, null=True)
    worksite =models.TextField(null=True,blank=True)
    month =models.TextField(null=True,blank=True)
    year =models.TextField(null=True,blank=True)
    file_name = models.TextField(null=True, blank=True)
    checksum_message = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    error_count = models.TextField(null=True, blank=True)
    update_count = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='checksum_created_by',blank=True, null=True,db_column='created_by')

    class Meta:
        db_table = 'file_checksum'


class file_errorlog(models.Model):
    error_id = models.AutoField(primary_key=True)
    upload_for =models.TextField(null=True,blank=True)
    company = models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='errorlog_company',blank=True, null=True)
    worksite =models.TextField(null=True,blank=True)
    file_name = models.TextField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    checksum = models.ForeignKey(file_checksum, on_delete=models.CASCADE,related_name='checksum1_created_by',blank=True, null=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='file_errorlog_created_by',blank=True, null=True,db_column='created_by')

    class Meta:
        db_table = 'file_errorlog'    
    
class sc_roster(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id =models.TextField(null=True,blank=True)
    employee_name =models.TextField(null=True,blank=True)
    company = models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='roster_company',blank=True, null=True)
    worksite =models.TextField(null=True,blank=True)
    shift_date = models.DateField(null=True,blank=True)
    shift_time = models.TextField(null=True,blank=True)
    confirmation = models.BooleanField(null=True,blank=True,default=False)
    confirmation_date = models.DateTimeField(null=True,blank=True)
    attendance_in = models.TextField(null=True,blank=True)
    attendance_out = models.TextField(null=True,blank=True)
    attendance_date = models.DateTimeField(null=True,blank=True)
    checksum = models.ForeignKey(file_checksum, on_delete=models.CASCADE,related_name='checksum_roster',blank=True, null=True)
    uploaded_date = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='uploaded_by',blank=True, null=True,db_column='uploaded_by')
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='roster_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='roster_updated_by',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'sc_roster'
    def __str__(self):
        return self.employee_id


        
class Log(models.Model):
    log_text = models.TextField(null=True,blank=True)
    class Meta:
        db_table = 'logs'