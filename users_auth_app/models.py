from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    file = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.username


class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tel = models.CharField(max_length=30)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Business: {self.user.username}"
    

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Customer: {self.user.username}"