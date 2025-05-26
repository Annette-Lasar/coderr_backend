from rest_framework import serializers
from ..models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model, handling all fields.
    Ensures that the reviewer field is read-only and set automatically.
    """

    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
