from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfileModel(models.Model):
    """
    Model representing an extended user profile.
    Stores additional user details like profile picture, location, availability, and user type (business or customer).
    """

    USER_TYPES = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255, default="default")
    file = models.FileField(
        upload_to='profile_pics/', null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    tel = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    availability = models.CharField(max_length=50, null=True, blank=True)
    user_type = models.CharField(
        max_length=10, choices=USER_TYPES, default='customer')

    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username
