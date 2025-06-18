from rest_framework import serializers
from .models import Order, Offer, CartItem
from accounts.serializers import UserSerializer, AddressSerializer
from products.serializers import ProductSerializer

class OfferSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    buyer_processing_fee = serializers.SerializerMethodField()
    buyer_shipping_fee = serializers.SerializerMethodField()
    buyer_total_price = serializers.SerializerMethodField()
    seller_transaction_fee = serializers.SerializerMethodField()
    seller_processing_fee = serializers.SerializerMethodField()
    seller_shipping_fee = serializers.SerializerMethodField()
    seller_net_amount = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'product', 'offer_type', 'price', 'quantity', 'condition', 'stock',
            'buyer_processing_fee', 'buyer_shipping_fee', 'buyer_total_price',
            'seller_transaction_fee', 'seller_processing_fee', 'seller_shipping_fee', 'seller_net_amount',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_stock(self, value):
        if self.initial_data.get('offer_type') == Offer.OFFER_TYPE_SELL and (value is None or value <= 0):
            raise serializers.ValidationError("Stock must be greater than 0 for sell offers.")
        return value

    def get_buyer_processing_fee(self, obj):
        base_price = obj.price * obj.quantity
        return max(base_price * 0.06, 5.00)

    def get_buyer_shipping_fee(self, obj):
        return 10.00

    def get_buyer_total_price(self, obj):
        base_price = obj.price * obj.quantity
        buyer_processing_fee = max(base_price * 0.06, 5.00)
        buyer_shipping_fee = 10.00
        return base_price + buyer_processing_fee + buyer_shipping_fee

    def get_seller_transaction_fee(self, obj):
        base_price = obj.price * obj.quantity
        return max(base_price * 0.09, 5.00)

    def get_seller_processing_fee(self, obj):
        base_price = obj.price * obj.quantity
        return base_price * 0.03

    def get_seller_shipping_fee(self, obj):
        return 10.00

    def get_seller_net_amount(self, obj):
        base_price = obj.price * obj.quantity
        seller_transaction_fee = max(base_price * 0.09, 5.00)
        seller_processing_fee = base_price * 0.03
        seller_shipping_fee = 10.00
        return base_price - seller_transaction_fee - seller_processing_fee - seller_shipping_fee

class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    seller = UserSerializer(read_only=True)  # Ajouté
    offer = OfferSerializer(read_only=True)
    buyer_address = AddressSerializer(read_only=True)
    seller_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'seller', 'offer', 'quantity', 'base_price',
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
        offer = self.initial_data.get('offer')
        if offer:
            from .models import Offer
            offer_obj = Offer.objects.get(id=offer)
            if offer_obj.offer_type == Offer.OFFER_TYPE_SELL and value > offer_obj.stock:
                raise serializers.ValidationError("Quantity exceeds available stock.")
            if offer_obj.offer_type == Offer.OFFER_TYPE_BUY and value > offer_obj.quantity:
                raise serializers.ValidationError("Quantity exceeds offer quantity.")
        return value

    def validate_buyer_address(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("Buyer address must belong to the buyer.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'offer', 'quantity', 'reserved_until', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reserved_until', 'created_at', 'updated_at']
