from rest_framework import serializers
from users_auth_app.models import UserProfileModel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.conf import settings


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profiles, combining user and profile fields.
    Includes file upload handling and provides the full file URL.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(
        source="user.first_name", required=False)
    last_name = serializers.CharField(
        source="user.last_name", required=False)
    type = serializers.CharField(source='user_type')
    working_hours = serializers.CharField(
        source='availability', required=False, default="")

    file = serializers.SerializerMethodField()

    class Meta:
        model = UserProfileModel
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        user = instance.user
        if "username" in user_data:
            user.username = user_data["username"]
        if "first_name" in user_data:
            user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            user.last_name = user_data["last_name"]
        if "email" in validated_data:
            email = validated_data.pop("email")
            user.email = email
            instance.email = email
        user.save()

        return super().update(instance, validated_data)

    def get_file(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None


class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    Handles validation of username, email, and password confirmation.
    """

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, min_length=6)
    repeated_password = serializers.CharField(
        write_only=True, required=True, min_length=6)
    type = serializers.ChoiceField(
        choices=UserProfileModel.USER_TYPES, default='customer')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Dieser Benutzername ist bereits vergeben.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Diese E-Mail-Adresse wird bereits verwendet.")
        return value

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"repeated_password": "Die Passwörter stimmen nicht überein."})
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials, authenticates the user, and returns 
    an authentication token.
    """

    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            raise serializers.ValidationError(
                {"detail": ["Benutzername und Passwort sind erforderlich."]})

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                {"detail": ["Ungültige Anmeldeinformationen."]})

        token, created = Token.objects.get_or_create(user=user)

        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }


class BusinessUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing business users.
    Includes selected profile and user details, along with profile image and availability.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    file = serializers.SerializerMethodField()
    working_hours = serializers.CharField(
        source='availability', required=False)
    type = serializers.CharField(source='user_type')

    class Meta:
        model = UserProfileModel
        fields = ['user', 'username', 'first_name', 'last_name', 'file',
                  'location', 'tel', 'description', 'working_hours', 'type']

    def get_file(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None


class CustomerUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing customer users.
    Includes selected profile and user details, profile image, registration date, and user type.
    """

    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    file = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()
    type = serializers.CharField(source='user_type')

    class Meta:
        model = UserProfileModel
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type'
        ]

    def get_file(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None

    def get_uploaded_at(self, obj):
        return obj.created_at
