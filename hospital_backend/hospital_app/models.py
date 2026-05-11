from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

# ================================
# Custom User for Hospital Service
# ================================

class HospitalUserManager(BaseUserManager):
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


class HospitalUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = HospitalUserManager()

    def __str__(self):
        return self.email

# ================================
# Hospital
# ================================

class Hospital(models.Model):
    user = models.OneToOneField(HospitalUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True)
    region = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ================================
# Blood Requests
# ================================

class BloodRequest(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=5)
    request_date = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True)
    status = models.CharField(
        max_length=20,
        choices=[('open','open'),('fulfilled','fulfilled'),('expired','expired')],
        default='open'
    )
    quantity_needed = models.IntegerField(default=1)
    description = models.TextField(null=True)

# ================================
# Donation (Hospital View)
# ================================

class Donation(models.Model):
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE)
    donor_id = models.IntegerField()  # Received from donor service
    donation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending','pending'),('approved','approved'),('rejected','rejected'),('completed','completed')],
        default='pending'
    )

# ================================
# Campaign
# ================================

class Campaign(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    starting_date = models.DateField(null=True)
    ending_date = models.DateField(null=True)
    address = models.CharField(max_length=255, null=True)
    duration = models.CharField(max_length=100, null=True)
    poster_image = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
