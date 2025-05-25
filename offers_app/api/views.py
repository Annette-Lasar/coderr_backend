from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min

from offers_app.models import Offer, OfferDetail
from offers_app.api.serializers import OfferSerializer, OfferDetailsSerializer

from utils.pagination import SixPerPagePagination
from utils.permissions import IsBusinessOwnerOrAdmin


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [IsAuthenticated, IsBusinessOwnerOrAdmin]
    pagination_class = SixPerPagePagination

    filterset_fields = {
        'creator': ['exact'],
        'offer_details__price': ['gte'],
        'offer_details__delivery_time_in_days': ['lte'],
    }
    search_fields = ['title', 'description']
    ordering_fields = ['min_price']

    def get_queryset(self):
        queryset = self.queryset.annotate(
            min_price=Min('offer_details__price'),
            min_delivery_time=Min('offer_details__delivery_time_in_days')
        )

        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(creator_id=creator_id)

        if not self.request.query_params.get('ordering'):
            queryset = queryset.order_by('-created_at')

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailViewSet(viewsets.ModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailsSerializer
