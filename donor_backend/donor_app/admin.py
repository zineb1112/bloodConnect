from django.contrib import admin

# Register your models here.
from .models import DonorUser, Donor, Notification

admin.site.register(DonorUser)
admin.site.register(Donor)
admin.site.register(Notification)
