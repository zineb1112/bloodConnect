from django.contrib import admin

# Register your models here.
from .models import HospitalUser, Hospital, BloodRequest, Donation, Campaign

admin.site.register(HospitalUser)
admin.site.register(Hospital)
admin.site.register(BloodRequest)
admin.site.register(Donation)
admin.site.register(Campaign)