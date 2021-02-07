from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# from .models import UserProfile
# from user_app.models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    standard_fieldsets = list(UserAdmin.fieldsets)[:]
    print('standard = ', standard_fieldsets)
    fieldsets = standard_fieldsets.append((None, {'fields': ['bio']}))


admin.site.register(User, CustomUserAdmin)
