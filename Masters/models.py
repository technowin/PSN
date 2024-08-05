from django.db import models

# Create your models here.

from django.db import models


# Create your models here.
class Unit(models.Model):
    CompanyName = models.CharField(max_length=255)
    UnitName = models.CharField(max_length=255)
    UnitAddress =models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)

    def __str__(self):
        return self.CompanyName
class UnitEdit(models.Model):
    locationid =models.IntegerField()
    companyname = models.CharField(max_length=255)
    statename = models.CharField(max_length=255)
    locationname =models.CharField(max_length=255)
    governmentname =models.CharField(max_length=255)
    establishmentname =models.CharField(max_length=255)
    establishmentaddress =models.CharField(max_length=255)
    directorname1 =models.CharField(max_length=255)
    directorname2 =models.CharField(max_length=255)
    directorname3 =models.CharField(max_length=255)
    directorname4 =models.CharField(max_length=255)
    directorname5 =models.CharField(max_length=255)
    managername =models.CharField(max_length=255)
    gratuityact =models.CharField(max_length=255)
    persondesignation =models.CharField(max_length=255)
    natureofbuisness =models.CharField(max_length=255)
    maleempcount =models.IntegerField()
    femaleempcount =models.IntegerField()
    empthrucontractor =models.IntegerField()
    closuredate=models.DateField()
    horsepower =models.IntegerField()
    remarks =models.CharField(max_length=255)
    officeshopexistence =models.CharField(max_length=255)
    status =models.IntegerField()
    namestate =models.CharField(max_length=255)
    namecompany =models.CharField(max_length=255)

    

    def __str__(self):
        return self.companyname
    

class State(models.Model):
    stateid = models.IntegerField()
    statename = models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)

    def __str__(self):
        return self.statename
    
# class Location(models.Model):
#     location_id = models.IntegerField()
#     statename = models.CharField(max_length=255)
#     company_name = models.CharField(max_length=255)
#     location_name = models.CharField(max_length=255)
#     Encryp =models.CharField(max_length=255)

#     def __str__(self):
#         return self.location_name

class Government(models.Model):
    govid = models.IntegerField()
    govname = models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)
    status = models.IntegerField()

    def __str__(self):
        return self.govname
class LicenseType(models.Model):
    Licensetypeid = models.IntegerField()
    Licensename = models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)
    status = models.IntegerField()

    def __str__(self):
        return self.Licensename
class LocationLicense(models.Model):
    LocLicenseid = models.IntegerField()
    Locationname = models.CharField(max_length=255)
    Licensename = models.CharField(max_length=255)
    RegistrationNo = models.IntegerField()
    RegistrationDate = models.DateField()
    ValidUptoDate = models.DateField()
    NextRenewalDueDate = models.DateField()   
    ContractorId = models.CharField(max_length=255) 
    companyid = models.CharField(max_length=255) 
    companyname = models.CharField(max_length=255) 
    is_license_uploaded = models.CharField(max_length=255) 
    Encryp = models.CharField(max_length=255)


    def __str__(self):
        return self.Locationname        
class location(models.Model):
    name =  models.CharField(max_length=200)
    email =  models.CharField(max_length=200)
    marks =  models.CharField(max_length=200)
    locationid = models.IntegerField()
    statename = models.CharField(max_length=255)
    companyname = models.CharField(max_length=255)
    locationname = models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)
class Company(models.Model):
    CompanyName = models.CharField(max_length=255)
    CompanyNameShort = models.CharField(max_length=255)
    company_name_short = models.CharField(max_length=255)
    CompanyAddress = models.CharField(max_length=255)
    SrNo =models.CharField(max_length=255)
    contact_person_name =models.CharField(max_length=255)
    contact_person_email =models.CharField(max_length=255)
    contact_person_mobileno =models.CharField(max_length=255)
    pf_payment_day =models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)
    Encryp1 =models.CharField(max_length=255)
    def __str__(self):
        return str(self.type)
class Role(models.Model):
    roleid = models.IntegerField()
    rolename = models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)

    def __str__(self):
        return self.rolename
class UserRole(models.Model):
    tableid = models.IntegerField()
    userid = models.IntegerField()
    roleid = models.IntegerField()
    username = models.CharField(max_length=255)
    rolename = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    status = models.IntegerField()
    Encryp =models.CharField(max_length=255)

    def __str__(self):
        return self.username  
class ContractorRegData(models.Model):
    # govid = models.IntegerField()
    contractor_registration_id = models.IntegerField()
    contractor_name = models.CharField(max_length=255)
    location_license_id = models.CharField(max_length=255)
    contract_start_date =models.CharField(max_length=255)
    contract_end_date = models.CharField(max_length=255)
    # contract_employee_count = models.CharField(max_length=255)
    contract_employee_count_male = models.CharField(max_length=255)
    contract_employee_count_female = models.CharField(max_length=255)
    location_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    is_tasklist_enabled = models.CharField(max_length=255)
    Encryp = models.CharField(max_length=255)
    def __str__(self):
        return self.contractor_name   
class locationdropdownspecial(models.Model):
    UnitName = models.CharField(max_length=255)
    SrNo =models.CharField(max_length=255)
    Encryp =models.CharField(max_length=255)   
class LocationUploadN(models.Model):
    location_id = models.CharField(max_length=255)
    company_id = models.CharField(max_length=255)
    state_id = models.CharField(max_length=255)
    location_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.location_id    
class DatContRegSmpL(models.Model):
    contractor_registration_id = models.CharField(max_length=255)
    location_license_id = models.CharField(max_length=255)
    contractor_name = models.CharField(max_length=255)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    contract_employee_count_male = models.CharField(max_length=255)
    contract_employee_count_female = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_id = models.CharField(max_length=255)
    def __str__(self):
        return self.contractor_registration_id   
class LicenseTypeL(models.Model):
    license_id = models.CharField(max_length=255)
    license_name = models.CharField(max_length=255)
    def __str__(self):
        return self.license_id          
class LocationTemplateMapping(models.Model):
    table_id = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    location_name = models.CharField(max_length = 255)
    company_name = models.CharField(max_length = 255)
    template_name = models.CharField(max_length = 255)
class Type(models.Model):
    type_id = models.CharField(max_length=255)
    type_name = models.CharField(max_length=255)
    status = models.CharField(max_length = 255)
    Encryp = models.CharField(max_length = 255)
class Privilege(models.Model):
    privilege_id = models.CharField(max_length=255)
    privilege_name = models.CharField(max_length=255)
    status = models.CharField(max_length = 255)
    Encryp = models.CharField(max_length = 255)
class UserDetails(models.Model):
    table_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    is_lkn_employee = models.CharField(max_length = 255)
    superior_id = models.CharField(max_length = 255)
    status = models.CharField(max_length = 255)
    created_by = models.CharField(max_length = 255)
    created_at = models.CharField(max_length = 255)
    updated_at = models.CharField(max_length = 255)
    updated_by = models.CharField(max_length = 255)
    Encryp = models.CharField(max_length = 255)
class UserList(models.Model):
    user_id =  models.CharField(max_length=255)
    full_name =  models.CharField(max_length=255)
    email =  models.CharField(max_length=255)
    Encryp =  models.CharField(max_length=255)
class UserType(models.Model):
    user_id =  models.CharField(max_length=255)
    type_name =  models.CharField(max_length=255)
    email =  models.CharField(max_length=255)
    Encryp =  models.CharField(max_length=255)
class UserPrivilege(models.Model):
    user_id =  models.CharField(max_length=255)
    privilege_name =  models.CharField(max_length=255)
    email =  models.CharField(max_length=255)
    Encryp =  models.CharField(max_length=255)
    
class UserCompanyLocation(models.Model):
    user_id =  models.CharField(max_length=255)
    full_name =  models.CharField(max_length=255)
    company_name =  models.CharField(max_length=255)
    location_name =  models.CharField(max_length=255)
    Encryp =  models.CharField(max_length=255)
    
class Conractor(models.Model):
    company_name =  models.CharField(max_length=255)
    location_name = models.CharField(max_length=255)
    contractor_name = models.CharField(max_length=255)
    period = models.CharField(max_length=255)

    company_id =  models.IntegerField()
 
class Users(models.Model):
    Userid =  models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    active = models.CharField(max_length=255)
    Encryp = models.CharField(max_length=255)
    
class Client(models.Model):
    client_name =  models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    client_address = models.CharField(max_length=255)
    client_short_name = models.CharField(max_length=255)
    Encryp1 = models.CharField(max_length=255)
    Encryp = models.CharField(max_length=255)
    
    