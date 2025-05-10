from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=[("business", "Business"), ("customer", "Customer")])

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        
    def validate(self, data):
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Die Passwörter stimmen nicht überein.")
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
