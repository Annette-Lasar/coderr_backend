from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from django.db.models.functions import Greatest
from rest_framework.exceptions import ValidationError
from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import (
    OfferSerializer,
    OfferDetailsSerializer,
    OfferCreateSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from utils.pagination import SixPerPagePagination
from utils.permissions import IsBusinessOwnerOrAdmin


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Offer objects.
    Provides list, create, retrieve, update, and delete operations.
    """
    queryset = Offer.objects.all()
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsBusinessOwnerOrAdmin]
    pagination_class = SixPerPagePagination

    filterset_fields = {
        'user': ['exact'],
        'offer_details__price': ['gte'],
        'offer_details__delivery_time_in_days': ['lte'],
    }
    search_fields = ['title', 'description']
    ordering_fields = ['min_price', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = self.queryset.annotate(
            min_price=Min('offer_details__price'),
            min_delivery_time=Min('offer_details__delivery_time_in_days'),
            latest_date=Greatest('created_at', 'updated_at')
        )

        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                min_price = float(min_price)
                queryset = queryset.filter(min_price__gte=min_price)
            except ValueError:
                pass

        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
            except ValueError:
                raise ValidationError(
                    {"max_delivery_time": "Must be an integer."})
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time)

        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        if not self.request.query_params.get('ordering'):
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return OfferCreateSerializer
        return OfferSerializer

    def perform_create(self, serializer):
        offer = serializer.save(user=self.request.user)

        offer = Offer.objects.prefetch_related(
            'offer_details').get(pk=offer.pk)
        self._prefetched_object = offer

    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        serializer = OfferCreateSerializer(
            self.get_object(), context={'request': request}
        )
        return Response(serializer.data)


class OfferDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing OfferDetail objects.
    Provides full CRUD operations for offer details.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailsSerializer
    permission_classes = [IsAuthenticated]
