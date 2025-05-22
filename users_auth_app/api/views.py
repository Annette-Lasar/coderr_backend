from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from utils.pagination import SixPerPagePagination
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .serializers import (WrappedUserSerializer,
                          UserProfileSerializer,
                          RegistrationSerializer)


User = get_user_model()


# liefert das eigene Profil des eingeloggten Nutzers (z.B. laura)
class OwnProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({"user": serializer.data}) 

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"user": serializer.data})  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileDetailView(APIView):
    # oder IsAuthenticated, je nach Sichtbarkeit
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Benutzer nicht gefunden.'}, status=404)

        serializer = UserProfileSerializer(user)
        return Response({"user": serializer.data}) 

class BusinessProfileListView(APIView):
    def get(self, request):
        users = User.objects.filter(
            user_type='business').order_by('-created_at')
        paginator = SixPerPagePagination()
        result_page = paginator.paginate_queryset(users, request)
        wrapped_users = [{"user": u} for u in result_page]
        serializer = WrappedUserSerializer(wrapped_users, many=True)
        return Response(serializer.data)


class CustomerProfileListView(APIView):
    def get(self, request):
        users = User.objects.filter(
            user_type='customer').order_by('-created_at')
        paginator = SixPerPagePagination()
        result_page = paginator.paginate_queryset(users, request)
        wrapped_users = [{"user": u} for u in result_page]
        serializer = WrappedUserSerializer(wrapped_users, many=True)
        return Response(serializer.data)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Ungültiger Benutzername oder Passwort."},
                status=status.HTTP_401_UNAUTHORIZED
            )
