from rest_framework import serializers
from .models import User, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'name', 'street_number', 'street', 'city', 'state', 'postal_code',
            'country', 'phone_number', 'address_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        user = self.context['request'].user
        if data.get('address_type') in ['billing', 'both']:
            # Vérifier si une adresse de facturation existe déjà
            existing_billing = Address.objects.filter(user=user, address_type__in=['billing', 'both']).exclude(id=self.instance.id if self.instance else None)
            if existing_billing.exists():
                raise serializers.ValidationError({"address_type": "L'utilisateur a déjà une adresse de facturation."})
        return data

class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    billing_address = AddressSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'phone_number', 'is_buyer',
            'is_seller', 'is_verifier', 'billing_address', 'addresses'
        ]
        read_only_fields = ['id', 'is_buyer', 'is_seller', 'is_verifier']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user