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
        user.encrypted_password = user.password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    title = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    encrypted_password = models.CharField(max_length=128)  # Adjust the max_length as needed
    phone = models.CharField(max_length=15)  # Adjust the max_length as needed
    first_time_login = models.IntegerField(default=1)  # 1 for True, 0 for False
    last_login = models.DateTimeField(default=timezone.now)
    password_text = models.CharField(max_length=128)  # Store unencrypted password (not recommended)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']  # Add any additional required fields
    class Meta:
        db_table = 'users'
    def __str__(self):
        return self.email

class AssignedCompany(models.Model):
    company_name = models.CharField(max_length=255)
    company_id = models.CharField(max_length=255)


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    href = models.TextField()

    def __str__(self):
        return self.name