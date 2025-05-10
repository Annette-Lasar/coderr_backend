from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('business', 'Business'),
        ('customer', 'Customer')
    ]

    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="customer")
    file = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    tel = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
