from rest_framework import generics
from users_auth_app.models import UserProfileModel
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound

from .serializers import (UserProfileSerializer,
                          BusinessUserListSerializer,
                          CustomerUserListSerializer,
                          RegistrationSerializer,
                          LoginSerializer)


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve or update a user profile.
    Ensures users can only edit their own profile unless they are staff.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        user_id = self.kwargs["pk"]
        try:
            obj = UserProfileModel.objects.get(user__id=user_id)
            return obj
        except UserProfileModel.DoesNotExist:
            raise NotFound(f"UserProfile with user_id={user_id} not found.")

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_staff and obj.user != request.user:
            raise PermissionDenied("You can only edit your own profile.")
        return super().update(request, *args, **kwargs)


class BusinessUserListView(generics.ListAPIView):
    """
    API view to list all business user profiles.
    Accessible only to authenticated users.
    """

    serializer_class = BusinessUserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfileModel.objects.filter(user_type='business')


class CustomerUserListView(generics.ListAPIView):
    """
    API view to list all customer user profiles.
    Accessible only to authenticated users.
    """

    serializer_class = CustomerUserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfileModel.objects.filter(user_type='customer')


class RegistrationView(APIView):
    """
    API view to handle user registration.
    Allows any user to create a new account and returns an 
    authentication token upon success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            type = serializer.validated_data.get('type', 'customer')

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            UserProfileModel.objects.create(
                user=user,
                email=email,
                user_type=type,
                name=username,
            )
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view to handle user login.
    Authenticates the provided credentials and returns a token if valid.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
