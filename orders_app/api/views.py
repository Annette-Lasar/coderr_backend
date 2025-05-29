from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from orders_app.models import Order
from orders_app.api.serializers import (
    OrderSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
)
from rest_framework.permissions import IsAuthenticated
from utils.permissions import IsCustomerOrAdmin, IsAdminOnly
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from utils.permissions import IsBusinessOwnerOrAdmin, IsBusinessOrAdmin


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Order instances.
    Allows customers to create orders and both customers and business 
    users to view or update their associated orders. 
    Applies different serializers depending on the action.
    """

    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            raise NotAuthenticated(
                "Authentication credentials were not provided.")

        if user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )

    def get_permissions(self):
        if self.action in ['create']:
            return [IsCustomerOrAdmin()]
        if self.action == 'partial_update':
            return [IsBusinessOwnerOrAdmin()]
        if self.action == 'destroy':
            return [IsAdminOnly()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return CreateOrderSerializer
        if self.action == 'partial_update':
            return UpdateOrderStatusSerializer
        return OrderSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        """ Ensure only customers can create orders and assign the customer user """
        user_profile = getattr(self.request.user, 'profile', None)
        if not user_profile or user_profile.user_type != 'customer':
            raise PermissionDenied("Only customers can create orders.")

        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        if 'status' not in request.data:
            return Response(
                {"detail": "Das Feld 'status' ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST
            )

        super().partial_update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = OrderSerializer(
            instance, context=self.get_serializer_context())
        return Response(serializer.data)


class OrderCountView(APIView):
    """
    API view that returns the count of in-progress orders for a 
    given business user. Accepts a business_user_id as a URL parameter 
    and returns the count in the response.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)
        order_count = Order.objects.filter(
            business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    API view that returns the count of completed orders for a given 
    business user. Takes business_user_id as a URL parameter and 
    responds with the count.
    """
    permission_classes = [IsBusinessOrAdmin]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)
        completed_order_count = Order.objects.filter(
            business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)
