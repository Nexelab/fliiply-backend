from rest_framework import serializers
from .models import Product, Category, PriceHistory
import re

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['slug']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")
        return value

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'recorded_at']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    price_histories = PriceHistorySerializer(many=True, read_only=True)
    similar_products = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'set', 'name', 'image', 'description', 'average_price', 'total_stock', 'category', 'created_at', 'updated_at', 'price_histories', 'similar_products']

    def get_similar_products(self, obj):
        similar_products = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:5]
        return ProductSerializer(similar_products, many=True, context=self.context).data

    def get_average_price(self, obj):
        return obj.calculate_average_price()

    def get_total_stock(self, obj):
        return obj.calculate_total_stock()