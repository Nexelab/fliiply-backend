from rest_framework import serializers
from .models import Listing
from products.serializers import ProductSerializer
from accounts.serializers import UserSerializer

class ListingSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'product', 'seller', 'price', 'condition', 'stock', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be non-negative.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock must be non-negative.")
        return value