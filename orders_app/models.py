from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    customer_user = models.ForeignKey(
        User, related_name='orders_as_customer', on_delete=models.CASCADE
    )
    business_user = models.ForeignKey(
        User, related_name='orders_as_business', on_delete=models.CASCADE
    )
    offer_detail = models.ForeignKey(
        'offers_app.OfferDetail', on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.customer_user.profile.user_type != 'customer':
            raise ValidationError("Nur Kunden können Bestellungen aufgeben.")
        if self.business_user.profile.user_type != 'business':
            raise ValidationError("Nur Anbieter können Bestellungen erhalten.")

    def __str__(self):
        return f"Order #{self.id}: {self.title} by {self.customer_user.username} for {self.business_user.username}"
