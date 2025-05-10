from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Zusätzliche Infos', {
            'fields': ('user_type', 'file', 'tel', 'location', 'description', 'availability'),
        }),
    )
    
    list_display = (
        'username',
        'user_type', 
        'email',
        'first_name',
        'last_name',
        'is_staff',
    )
