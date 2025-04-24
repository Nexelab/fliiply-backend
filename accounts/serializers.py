from rest_framework import serializers
from .models import User, Address


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_buyer', 'is_seller', 'is_verifier']
        read_only_fields = ['id', 'is_buyer', 'is_seller', 'is_verifier']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'postal_code', 'country', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']