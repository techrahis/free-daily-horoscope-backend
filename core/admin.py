# admin.py
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _
from horoscopes.models import HoroscopeType, HoroscopeCategory, HoroscopeSign, Horoscope

class FreeDailyHoroscopeAdmin(admin.AdminSite):
    site_header = _('Free Daily Horoscope Admin')
    site_title = _('Free Daily Horoscope Admin')
    index_title = _('Welcome to Free Daily Horoscope Admin')

# Create an instance of the custom admin site
free_daily_horoscope_admin = FreeDailyHoroscopeAdmin(name='FreeDailyHoroscopeAdmin')

# Ensure the User model is registered with the custom admin site
free_daily_horoscope_admin.register(User, DefaultUserAdmin)

# Register Horoscope models with the custom admin site
free_daily_horoscope_admin.register(HoroscopeType)
free_daily_horoscope_admin.register(HoroscopeCategory)
free_daily_horoscope_admin.register(HoroscopeSign)
free_daily_horoscope_admin.register(Horoscope)