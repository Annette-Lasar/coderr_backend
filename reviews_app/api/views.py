from rest_framework import viewsets, filters, permissions
from ..models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from utils.permissions import IsCustomerOrAdmin, IsReviewerOrAdmin
from utils.pagination import SixPerPagePagination

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = SixPerPagePagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user', 'reviewer'] 
    ordering_fields = ['rating', 'created_at'] 

    def get_permissions(self):
        """Apply different permissions based on the action."""
        if self.action in ['create']:
            return [IsCustomerOrAdmin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsReviewerOrAdmin()]
        return [permissions.IsAuthenticated()]  

    def partial_update(self, request, *args, **kwargs):
        """Restrict editable fields to only 'rating' and 'description'."""
        allowed_fields = {'rating', 'description'}
        mutable_data = request.data.copy()
        request._full_data = {key: value for key, value in mutable_data.items() if key in allowed_fields}
        return super().partial_update(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Automatically assign the logged-in user as the reviewer."""
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        """Allow filtering by business_user_id manually"""
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        return queryset
