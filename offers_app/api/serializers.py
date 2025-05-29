from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.db.models import Min
from rest_framework.reverse import reverse as drf_reverse


class OfferDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail model. Serializes offer detail fields 
    for API responses.
    """
    price = serializers.FloatField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailsListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


class OfferDetailsRetrieveSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get('request')
        return drf_reverse('offerdetails-detail', args=[obj.id], request=request)


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
    image = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details',
        ]
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        details_data = self.initial_data.get('details', [])
        user = self.context["request"].user
        validated_data["user"] = user
        offer = Offer.objects.create(**validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

        return Offer.objects.prefetch_related('offer_details').get(pk=offer.pk)

    # def update(self, instance, validated_data):
    #     """Custom update method to allow partial updates and handle nested OfferDetails."""
    #     details_data = self.initial_data.get('details', None)

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()

    #     if details_data is not None:
    #         existing_details = {
    #             detail.offer_type: detail for detail in instance.offer_details.all()
    #         }

    #         for detail_data in details_data:
    #             offer_type = detail_data.get("offer_type")
    #             if offer_type in existing_details:
    #                 detail_instance = existing_details[offer_type]
    #                 for attr, value in detail_data.items():
    #                     if attr != 'offer_type':
    #                         setattr(detail_instance, attr, value)
    #                 detail_instance.save()
    #             else:
    #                 OfferDetail.objects.create(offer=instance, **detail_data)

    #     updated_offer = Offer.objects.prefetch_related(
    #         'offer_details').get(pk=instance.pk)
    #     return updated_offer

    def update(self, instance, validated_data):
        details_data = self.initial_data.get('details', None)

        # Aktualisiere Felder am Offer selbst
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {
                detail.offer_type: detail for detail in instance.offer_details.all()
            }

            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")

                if not offer_type:
                    raise serializers.ValidationError(
                        "Each detail must include an 'offer_type' field to be properly matched."
                    )

                if offer_type in existing_details:
                    detail_instance = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        if attr != 'offer_type':
                            setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        is_detail = request and 'pk' in request.parser_context.get(
            'kwargs', {})

        if is_detail:
            representation.pop('user_details', None)

        return representation

    def get_details(self, obj):
        request = self.context.get("request")
        view = self.context.get("view")

        if request and request.method == "POST":
            return OfferDetailsSerializer(obj.offer_details.all(), many=True).data

        if view and view.action == 'retrieve':
            return OfferDetailsRetrieveSerializer(obj.offer_details.all(), many=True, context=self.context).data

        return OfferDetailsListSerializer(obj.offer_details.all(), many=True, context=self.context).data

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

    def get_image(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None


class OfferCreateSerializer(serializers.ModelSerializer):

    details = OfferDetailsSerializer(
        source='offer_details', many=True, read_only=True)

    image = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def get_image(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None
