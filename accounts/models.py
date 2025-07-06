from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
import random


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Telefon raqam kiritilishi kerak')
        extra_fields.setdefault('is_active', True)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('free', 'Free User'),
        ('premium', 'Premium User'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13, unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='free')


    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


    def __str__(self):
        return self.phone_number


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    profile_img = models.ImageField(upload_to='profile_img', null=True, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    balance = models.PositiveIntegerField(default=0)

    def is_free_user(self):
        return self.user.role == 'free'

    def is_paid_user(self):
        return self.user.role == 'paid'

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.full_name


class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=13, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    resend_time = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    attempt_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)

    def is_locked(self):
        return self.locked_until and self.locked_until > timezone.now()

    def reset_attempts(self):
        if self.attempt_count >= 3 and self.locked_until and self.locked_until < timezone.now():
            self.attempt_count = 0
            self.locked_until = None
            self.save()

    def increment_attempts(self):
        self.attempt_count += 1
        if self.attempt_count == 3:
            self.locked_until = timezone.now() + timedelta(minutes=5)
        self.save()

    def is_expired(self):
        return self.created_at + timedelta(minutes=3) < timezone.now()

    def can_resend(self ):
        if not self.resend_time:
            return True
        return self.locked_until + timedelta(minutes=5) < timezone.now()

    @staticmethod
    def generate_otp():
        otp = str(random.randint(100000, 999999))
        return otp

    def __str__(self):
        return f"{self.phone_number} {self.otp}"
