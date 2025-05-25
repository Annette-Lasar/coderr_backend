from django.urls import path, include
from rest_framework import routers
from offers_app.api.views import OfferViewSet, OfferDetailViewSet

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet)
router.register(r'offerdetails', OfferDetailViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
