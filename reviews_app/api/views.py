from rest_framework import viewsets, filters, permissions, status
from ..models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from utils.permissions import IsCustomerOrAdmin, IsReviewerOrAdmin
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Review objects.
    Handles creation, listing, updating, and deleting of reviews 
    with proper permissions. Allows filtering by business_user or 
    reviewer and supports ordering by rating or date.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['business_user', 'reviewer']
    ordering_fields = ['rating', 'created_at', 'updated_at']

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
        filtered_data = {
            key: value for key, value in mutable_data.items() if key in allowed_fields}

        if 'rating' not in filtered_data or 'description' not in filtered_data:
            return Response(
                {"detail": "Both 'rating' and 'description' fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        request._full_data = filtered_data
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Automatically assign the logged-in user as the reviewer, but ensure only one review per business user."""
        reviewer = self.request.user
        business_user = serializer.validated_data.get('business_user')

        if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
            raise ValidationError(
                "Du hast bereits eine Bewertung für diesen Anbieter abgegeben.")

        serializer.save(reviewer=reviewer)

    def get_queryset(self):
        queryset = super().get_queryset()

        business_user_id = self.request.query_params.get('business_user_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        reviewer_id = self.request.query_params.get('reviewer_id')
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset
