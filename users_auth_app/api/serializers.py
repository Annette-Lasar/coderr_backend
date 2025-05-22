from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    tel = serializers.CharField(required=True)
    pk = serializers.IntegerField(source='id')
    type = serializers.CharField(source='user_type')
    working_hours = serializers.CharField(source='availability', required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'pk',
            'username',
            'email',
            'first_name',
            'last_name',
            'type',
            'file',
            'tel',
            'location',
            'description',
            'working_hours',
            'created_at'
        ]
    
    def validate_tel(self, value):
        if not value:
            raise serializers.ValidationError("Telefonnummer ist erforderlich.")
        return value



class WrappedUserSerializer(serializers.Serializer):
    user = UserProfileSerializer()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=[("business", "Business"), ("customer", "Customer")])

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {
        'email': {'required': True},
    }

    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError(
                "Die Passwörter stimmen nicht überein.")
        return data

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        user_type = validated_data.pop("type")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.user_type = user_type
        user.set_password(password)
        user.save()

        return user
