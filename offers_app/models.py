import json
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.ImageField(upload_to='offer_pics/', null=True, blank=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='offers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ]

    offer = models.ForeignKey('Offer', on_delete=models.CASCADE, related_name='details')
    offer_type = models.CharField(max_length=30, choices=OFFER_TYPE_CHOICES, default='basic')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_in_days = models.PositiveIntegerField()
    features = models.JSONField(default=list, blank=True)
    revisions = models.IntegerField(default=0, help_text="Number revisions the customer is allowed to request. -1 for unlimited revisions")
    
    def __str__(self):
        return f"{self.offer.title} - {self.offer_type.capitalize()}"
    
