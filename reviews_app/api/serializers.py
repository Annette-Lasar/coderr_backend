from rest_framework import serializers
from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model, handling all fields.
    Ensures that the reviewer field is read-only and set automatically.
    """

    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        rating_value = float(instance.rating)
        if rating_value.is_integer():
            data['rating'] = int(rating_value)
        else:
            data['rating'] = rating_value
        return data
