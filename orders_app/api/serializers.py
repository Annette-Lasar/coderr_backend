from rest_framework import serializers
from django.shortcuts import get_object_or_404
from offers_app.models import OfferDetail
from ..models import Order


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model, exposing all fields including 
    customer, business, offer details, pricing, and delivery information.
    All fields are read-only to prevent client-side modifications.
    """

    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(read_only=True)
    revisions = serializers.IntegerField(read_only=True)
    delivery_time_in_days = serializers.IntegerField(read_only=True)
    price = serializers.SerializerMethodField()
    features = serializers.JSONField(read_only=True)
    offer_type = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]

    def get_price(self, obj):
        price_value = float(obj.price)
        if price_value.is_integer():
            return int(price_value)
        return price_value


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating a new Order instance from an existing 
    OfferDetail. Handles assigning the customer, business, and all 
    relevant offer details. Includes a custom representation to 
    return full order data after creation.
    """

    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        offer_detail = get_object_or_404(
            OfferDetail, id=validated_data['offer_detail_id'])
        offer = offer_detail.offer

        customer_user = self.context['request'].user
        business_user = offer.user

        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )
        return order

    def to_representation(self, instance):
        """Ensure the full order details are returned in the response."""
        return OrderSerializer(instance).data


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    """
    Serializer to update only the status field of an Order instance.
    """
    class Meta:
        model = Order
        fields = ['status']
