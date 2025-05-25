from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfileModel


@admin.register(UserProfileModel)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_type',
        'tel',
        'location',
        'availability',
        'created_at',
    )
    search_fields = ('user__username', 'user__email', 'tel', 'location')
    list_filter = ('user_type', 'created_at')
