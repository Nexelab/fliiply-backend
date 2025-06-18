from rest_framework import serializers
from .models import Order, CartItem
from accounts.serializers import UserSerializer, AddressSerializer
from products.serializers import ListingSerializer

class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)  # Ajouté
    listing = ListingSerializer(read_only=True)
    buyer_address = AddressSerializer(read_only=True)
    seller_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'seller', 'listing', 'quantity', 'base_price',
            'buyer_address', 'seller_address',
            'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
            'seller_transaction_fee', 'seller_processing_fee', 'seller_shipping_fee', 'seller_net_amount',
            'platform_commission', 'stripe_payment_intent_id',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'base_price', 'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
            'seller_transaction_fee', 'seller_processing_fee', 'seller_shipping_fee', 'seller_net_amount',
            'platform_commission', 'stripe_payment_intent_id',
            'created_at', 'updated_at'
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        listing = self.initial_data.get('listing')
        if listing:
            from products.models import Listing
            listing_obj = Listing.objects.get(id=listing)
            if value > listing_obj.stock:
                raise serializers.ValidationError("Quantity exceeds available stock.")
        return value

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
