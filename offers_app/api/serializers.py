from rest_framework import serializers
from django.db.models import Min
from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='offer.title', read_only=True)
    offer_id = serializers.IntegerField(source='offer.id', read_only=True)
    features = serializers.ListField(
        child=serializers.CharField(), required=False)

    class Meta:
        model = OfferDetail
        fields = ['id', 'offer_id', 'offer_type', 'title', 'price',
                  'delivery_time_in_days', 'revisions', 'features']


class OfferSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(source='creator', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'description',
            'image',
            'min_price',
            'min_delivery_time',
            'created_at',
            'updated_at',
            'details',
            'user'
        ]

    def get_image(self, obj):
        try:
            if obj.file and obj.file.name and not obj.file.name.endswith('/'):
                return f"media/{obj.file.name}"
        except (ValueError, AttributeError):
            return None

    def get_details(self, obj):
        details = OfferDetail.objects.filter(
            offer=obj).exclude(id__isnull=True)
        return OfferDetailSerializer(details, many=True).data

    def get_min_price(self, obj):
        min_price = obj.details.aggregate(Min('price'))['price__min']
        return min_price

    def get_min_delivery_time(self, obj):
        min_delivery_time = obj.details.aggregate(Min('delivery_time_in_days'))[
            'delivery_time_in_days__min']
        return min_delivery_time
