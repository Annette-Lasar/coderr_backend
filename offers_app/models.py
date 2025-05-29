import json
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Offer(models.Model):
    """
    Model representing a freelance offer, including title, description, 
    optional image file, creator (user), and timestamps for creation 
    and last update.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='offer_pics/', null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='offers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class OfferDetail(models.Model):
    """
    Model representing the details of an offer variation (Basic, Standard, 
    Premium), including title, price, delivery time, features, and 
    allowed revisions.
    """
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ]

    offer = models.ForeignKey(
        'Offer', on_delete=models.CASCADE, related_name='offer_details')
    title = models.CharField(max_length=255, default="Untitled Detail")
    offer_type = models.CharField(
        max_length=30, choices=OFFER_TYPE_CHOICES, default='basic')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_in_days = models.PositiveIntegerField()
    features = models.JSONField(default=list, blank=True)
    revisions = models.IntegerField(
        default=0, help_text="Number revisions the customer is allowed to request. -1 for unlimited revisions")

    def __str__(self):
        return f"{self.offer.title} - {self.offer_type.capitalize()}"
