from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from django.db.models.functions import Greatest

from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailsSerializer
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from utils.pagination import SixPerPagePagination
from utils.permissions import IsBusinessOwnerOrAdmin


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Offer objects.
    Provides list, create, retrieve, update, and delete operations 
    for offers. Supports filtering by creator, minimum price, and 
    maximum delivery time; searching by title and description; and 
    ordering by minimum price, creation date, or update date.
    """ 
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticated, IsBusinessOwnerOrAdmin]
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

        max_delivery_time = self.request.query_params.get('max_delivery_time')
        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
                queryset = queryset.filter(
                    min_delivery_time__lte=max_delivery_time)
            except ValueError:
                pass

        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        if not self.request.query_params.get('ordering'):
            queryset = queryset.order_by('-created_at')

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing OfferDetail objects.
    Provides full CRUD operations for offer details.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailsSerializer
