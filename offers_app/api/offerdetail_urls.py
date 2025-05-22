from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferDetailViewSet

router = DefaultRouter()
router.register(r'', OfferDetailViewSet, basename='offerdetails') 

urlpatterns = [
    path('', include(router.urls)),
]
