from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.db.models import Min
from django.urls import reverse
from django.conf import settings


class OfferDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail model. Serializes offer detail fields 
    for API responses.
    """
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailsGETSerializer(serializers.ModelSerializer):
    """Serializer for GET requests: returns only ID and URL."""
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        url = reverse('offerdetails-detail', args=[obj.id])
        return url.replace('/api', '')


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for the Offer model. Includes related user details, 
    offer details, image handling, and computed fields like minimum 
    price and delivery time. Handles nested creation and updates of 
    OfferDetails.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    min_price = serializers.FloatField(read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)

    file = serializers.FileField(required=False)
    image = serializers.FileField(source='file', required=False)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'user_details',
            'title',
            'description',
            'details',
            'file',
            'image',
            'image_url',
            'created_at',
            'updated_at',
            'min_price',
            'min_delivery_time'
        ]
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        """Custom create method to handle nested offer details."""
        details_data = self.initial_data.get('details', [])

        if len(details_data) != 3:
            raise serializers.ValidationError(
                "Es müssen genau drei Details übergeben werden.")

        user = self.context["request"].user
        validated_data["user"] = user
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        """Custom update method to allow partial updates and handle nested OfferDetails."""
        details_data = self.initial_data.get('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {
                detail.offer_type: detail for detail in instance.offer_details.all()
            }

            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")
                if offer_type in existing_details:
                    detail_instance = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        if attr != 'offer_type':
                            setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)

        return instance

    def get_details(self, obj):
        """Return different detail structures for list vs single offer requests."""
        request = self.context.get("request")

        if request and (request.parser_context.get("kwargs", {}).get("pk") or request.method == "POST"):
            return OfferDetailsSerializer(obj.offer_details.all(), many=True).data

        return OfferDetailsGETSerializer(obj.offer_details.all(), many=True).data

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }

    def get_min_price(self, obj):
        min_price = obj.offer_details.aggregate(
            min_price=Min('price'))['min_price']
        return float(min_price) if min_price is not None else 0.00

    def get_min_delivery_time(self, obj):
        min_time = obj.offer_details.aggregate(
            min_time=Min('delivery_time_in_days'))['min_time']
        return min_time if min_time is not None else 0

    def get_image_url(self, obj):
        """Ensure image URL includes MEDIA_URL"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            else:
                return f"{settings.MEDIA_URL}{obj.file}"
        return None
