from django.db import models

# Create your models here.

from django.db import models

from Account.models import CustomUser


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
    roster_type = models.ForeignKey(parameter_master, on_delete=models.CASCADE,related_name='company_relation',blank=True, null=True,db_column='roster_type')
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
    current_location =models.TextField(null=True,blank=True)
    employee_status =models.TextField(null=True,blank=True)
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
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'application_search'
    def __str__(self):
        return self.name
    
    
class sc_roaster(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id =models.TextField(null=True,blank=True)
    site = models.ForeignKey(site_master, on_delete=models.CASCADE,related_name='site',blank=True, null=True)
    shift_date = models.DateField(null=True,blank=True)
    shift_from = models.TimeField(null=True,blank=True)
    shift_to = models.TimeField(null=True,blank=True)
    uploaded_date = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='uploaded_by',blank=True, null=True,db_column='uploaded_by')
    
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='updated_by',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'sc_roaster'
    def __str__(self):
        return self.employee_id
    
    