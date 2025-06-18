from rest_framework import serializers
from .models import Order, CartItem, OrderItem
from accounts.serializers import UserSerializer, AddressSerializer
from products.serializers import ListingSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'listing', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'items', 'base_price',
            'buyer_address',
            'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
            'platform_commission', 'stripe_payment_intent_id',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'base_price', 'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
            'platform_commission', 'stripe_payment_intent_id',
            'created_at', 'updated_at'
        ]

    def validate_buyer_address(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Buyer address must belong to the buyer.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'listing', 'quantity', 'reserved_until', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reserved_until', 'created_at', 'updated_at']
