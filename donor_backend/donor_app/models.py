from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

# ================================
# Custom User for Donor Service
# ================================

class DonorUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class DonorUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = DonorUserManager()

    def __str__(self):
        return self.email

# ================================
# Donor
# ================================

class Donor(models.Model):
    user = models.OneToOneField(DonorUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=10, null=True)
    blood_type = models.CharField(max_length=5, null=True)
    region = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    weight = models.IntegerField(null=True)
    image_url = models.TextField(null=True)
    availability = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ================================
# Notification
# ================================

class Notification(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    request_id = models.IntegerField()   # comes from HOSPITAL service 
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.donor.full_name}"
