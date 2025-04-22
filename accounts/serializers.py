from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_buyer', 'is_seller', 'is_verifier']
        read_only_fields = ['id', 'is_buyer', 'is_seller', 'is_verifier']