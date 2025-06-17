from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import User, Address
from accounts.services import create_stripe_account

User = get_user_model()

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
            'is_seller', 'is_verifier', 'billing_address', 'addresses', 'is_email_verified',
            'role', 'rating', 'stripe_account_id', 'is_kyc_verified'
        ]
        read_only_fields = [
            'id', 'is_buyer', 'is_verifier', 'is_email_verified',
            'rating', 'stripe_account_id', 'is_kyc_verified'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if validated_data.get('is_seller') and not user.stripe_account_id:
            create_stripe_account(user)
        if password:
            user.set_password(password)
            user.save()
        return user

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    accept_terms = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'phone_number', 'accept_terms', 'subscribed_to_newsletter', 'role']
        extra_kwargs = {
            'phone_number': {'required': False},  # Assurer que phone_number est facultatif
        }

    def validate(self, data):
        # Vérifier que les mots de passe correspondent
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})

        # Vérifier que les conditions générales sont acceptées
        if not data['accept_terms']:
            raise serializers.ValidationError({"accept_terms": "Vous devez accepter les conditions générales."})

        return data

    def create(self, validated_data):
        # Supprimer les champs temporaires
        validated_data.pop('confirm_password')
        validated_data.pop('accept_terms')
        role = validated_data.pop('role', User.Role.PARTICULIER)

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', None),
            subscribed_to_newsletter=validated_data.get('subscribed_to_newsletter', False),
            accepted_terms=True,
            accepted_terms_at=timezone.now(),
            role = role
        )

        if role == User.Role.PROFESSIONNEL:
            user.is_seller = True
            user.is_buyer = True
            create_stripe_account(user)
        else:
            user.is_seller = False  # Particulier ne peut pas vendre au départ
            user.is_buyer = True

        user.save()
        return user