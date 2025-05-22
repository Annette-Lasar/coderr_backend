from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from offers_app.models import Offer

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = {
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    }

    offer = models.ForeignKey('offers_app.Offer', on_delete=models.CASCADE)
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='in_progress')

    def clean(self):
        if self.customer.user_type != 'customer':
            raise ValidationError("Nur Kunden können Bestellungen aufgeben.")

        def __str__(self):
            return f"Bestellung von {self.customer.username} zu Angebot {self.offer.title}"
