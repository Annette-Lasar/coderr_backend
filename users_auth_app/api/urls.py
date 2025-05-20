from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (SingleUserProfileViewSet,
                    BusinessProfileViewSet,
                    CustomerProfileViewSet,
                    RegistrationView,
                    LoginView)

router = DefaultRouter()
router.register(r'profile', SingleUserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('profiles/business/',
         BusinessProfileViewSet.as_view({'get': 'list'})),
    path('profiles/customer/',
         CustomerProfileViewSet.as_view({'get': 'list'})),
    path('registration/', RegistrationView.as_view()),
    path('login/', LoginView.as_view()),
]
