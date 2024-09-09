# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# import bcrypt
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # user.password_text = password
        user.set_password(password)
        # user.encrypted_password = user.password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    # title = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # encrypted_password = models.CharField(max_length=225,null=True,blank=True)  # Adjust the max_length as needed
    phone = models.CharField(max_length=15,unique=True)
    first_time_login = models.IntegerField(default=1)  # 1 for True, 0 for False
    last_login = models.DateTimeField(default=timezone.now)
    # password_text = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    role = models.ForeignKey('Masters.Roles', on_delete=models.CASCADE, related_name='role_idd', blank=True, null=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']  # Add any additional required fields

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

class OTPVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_text = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'otp_verification'
        
class password_storage(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='user_id_repos',blank=True, null=True,db_column='created_by')
    passwordText =models.CharField(max_length=255,null=True,blank=True)
    class Meta:
        db_table = 'password_storage'

class error_log(models.Model):
    id = models.AutoField(primary_key=True)
    method =models.TextField(null=True,blank=True)
    error =models.TextField(null=True,blank=True)
    error_date = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='error_by',blank=True, null=True)
    class Meta:
        db_table = 'error_log'

    
     
class AssignedCompany(models.Model):
    company_name = models.CharField(max_length=255)
    company_id = models.CharField(max_length=255)


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    href = models.TextField()

    def __str__(self):
        return self.name

class FilesTest(models.Model):
    
    file_id = models.AutoField(primary_key=True)
    rec_id =  models.DateField(null=True,blank=True)
    rec_type =  models.CharField(max_length=255)
    file_name =  models.CharField(max_length=255)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='files_created',blank=True, null=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='files_updated',blank=True, null=True)
    class Meta:
        db_table = 'tbl_fileTest'


class user_role_map(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    role_id = models.BigIntegerField(null=True, blank=True)
    company_id = models.BigIntegerField(null=True, blank=True)
    worksite = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'user_role_map'
    def __str__(self):
        return f'User {self.user_id} - Role {self.role_id}'


class MenuMaster(models.Model):
    menu_id = models.AutoField(primary_key=True)
    menu_name = models.CharField(max_length=50, null=True, blank=True)
    menu_action = models.CharField(max_length=50, null=True, blank=True)
    menu_is_parent = models.BooleanField(null=True, blank=True)
    menu_parent_id = models.IntegerField(null=True, blank=True)
    menu_order = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    is_sub_menu = models.BooleanField(null=True, blank=True)
    sub_menu = models.IntegerField(null=True, blank=True)
    is_sub_menu2 = models.BooleanField(null=True, blank=True)
    sub_menu2 = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.TextField(null=True, blank=True)
    menu_icon = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'menu_master'


class UserMenuDetails(models.Model):
    user_menu_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, null=True, blank=True)
    menu_id = models.IntegerField(null=True, blank=True)
    role_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'user_menu_details'

class RoleMenuMaster(models.Model):
    role_menu_id = models.AutoField(primary_key=True)
    role_id = models.CharField(max_length=50, null=True, blank=True)
    menu_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'role_menu_master'

