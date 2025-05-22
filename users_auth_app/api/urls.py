from django.urls import path
from .views import (OwnProfileView,
                    UserProfileDetailView,
                    BusinessProfileListView,
                    CustomerProfileListView,
                    RegistrationView,
                    LoginView)


urlpatterns = [
    path('profile/', OwnProfileView.as_view(), name='own-profile'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfileListView.as_view(),
         name='business-profiles'),
    path('profiles/customer/', CustomerProfileListView.as_view(),
         name='customer-profiles'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
]
