from django.contrib import admin
from accounts.models import CustomUser, UserProfile, PhoneOTP


# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(PhoneOTP)