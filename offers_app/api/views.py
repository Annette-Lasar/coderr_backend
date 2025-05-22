from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from utils.pagination import SixPerPagePagination


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SixPerPagePagination

    def get_queryset(self):
        user = self.request.user

        if user.user_type == 'business':
            return Offer.objects.filter(creator=user).order_by('-updated_at')

        elif user.user_type == 'customer':
            return Offer.objects.all().order_by('-updated_at')

        return Offer.objects.none()



class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
