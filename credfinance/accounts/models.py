import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            force_password_change =True,
        )

        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        

        if password:
            
            user.set_password(password)
            user.save(using=self._db)

        user.save()
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=50,  blank=True, null=True)
    failed_login_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    force_password_change = models.BooleanField(default=True)
    has_changed_password = models.BooleanField(default=False)
    password_last_changed = models.DateTimeField(auto_now_add=True) 
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    groups = models.ManyToManyField(
    'auth.Group',
    related_name='account_groups',
    blank=True,
)
    user_type = models.CharField(max_length=255, default='general_user', choices=(('general_user', 'general_user'), ('administrator', 'administrator'), ('finance_manager', 'finance_manager')))
      

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def set_otp(self, otp):
        self.otp = otp
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.save(update_fields=['otp', 'otp_expiry'])

    def verify_otp(self, otp):
        if self.otp == otp and self.otp_expiry and timezone.now() < self.otp_expiry:
            self.otp = None
            self.otp_expiry = None
            self.save(update_fields=['otp', 'otp_expiry'])
            return True
        return False

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def set_password(self, raw_password):
        validate_password(raw_password, self)

        if self.pk:
            old_password = self.password
            PasswordHistory.objects.create(user=self, password=old_password)

        super().set_password(raw_password)
        self.password_last_changed = timezone.now()
        if self.has_changed_password:
            self.force_password_change = False
        self.save(update_fields=['password', 'password_last_changed', 'force_password_change'])

class PasswordHistory(models.Model):
    user = models.ForeignKey('Account', on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    timestamp = models.DateTimeField(default=timezone.now)