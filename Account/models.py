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
        user.password_text = password
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)  # Adjust the max_length as needed
    first_time_login = models.IntegerField(default=1)  # 1 for True, 0 for False
    last_login = models.DateTimeField(default=timezone.now)

    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']  # Add any additional required fields

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


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
        
class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    role_id = models.IntegerField(null=True, blank=False)
    role_name = models.TextField(null=True, blank=True)
    role_type = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='roles_created', blank=True, null=True, db_column='created_by')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='roles_updated', blank=True, null=True, db_column='updated_by')
    class Meta:
        db_table = 'roles'
