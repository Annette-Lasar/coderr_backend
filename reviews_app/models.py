# from django.db import models
# from django.core.exceptions import ValidationError
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class Review(models.Model):
#     author = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='given_reviews')
#     target = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='received_reviews')
#     rating = models.PositiveIntegerField(
#         validators=[MinValueValidator(1), MaxValueValidator(5)]
#     )
#     comment = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('author', 'target')

#     def clean(self):
#         if self.author.user_type != 'customer':
#             raise ValidationError("Nur Kunden dürfen Bewertungen schreiben.")
#         if self.target.user_type != 'business':
#             raise ValidationError("Nur Anbieter können bewertet werden.")
#         if self.author == self.target:
#             raise ValidationError("Man kann sich nicht selbst bewerten.")

#     def __str__(self):
#         return f"{self.author.username} → {self.target.username}: {self.rating} Sterne"


from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    business_user = models.ForeignKey(
        User, related_name='reviews_received', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(
        User, related_name='reviews_given', on_delete=models.CASCADE)
    rating = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
