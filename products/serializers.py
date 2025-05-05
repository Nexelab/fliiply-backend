from rest_framework import serializers
from .models import Product, Category, PriceHistory, ProductImage
from django.db.models import Q

class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children']
        read_only_fields = ['slug', 'children']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")
        return value

    def validate_parent(self, value):
        if value and self.instance and value == self.instance:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True, context=self.context).data

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'created_at']
        read_only_fields = ['created_at']

class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ['price', 'recorded_at']
        read_only_fields = ['recorded_at']

class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    categories_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source='categories'
    )
    images = ProductImageSerializer(many=True, read_only=True)
    price_histories = PriceHistorySerializer(many=True, read_only=True)
    similar_products = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'series', 'collection', 'description', 'tcg_type', 'language',
            'average_price', 'total_stock', 'categories', 'categories_ids',
            'images', 'created_at', 'updated_at', 'price_histories', 'similar_products'
        ]
        read_only_fields = ['created_at', 'updated_at', 'average_price', 'total_stock']

    def get_similar_products(self, obj):
        similar_products = Product.objects.filter(
            Q(categories__in=obj.categories.all()) |
            Q(tcg_type=obj.tcg_type) |
            Q(language=obj.language) |
            Q(series=obj.series)
        ).exclude(id=obj.id).distinct()[:5]
        return ProductSerializer(similar_products, many=True, context=self.context).data

    def get_average_price(self, obj):
        return obj.calculate_average_price()

    def get_total_stock(self, obj):
        return obj.calculate_total_stock()

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        product = Product.objects.create(**validated_data)
        product.categories.set(categories)
        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        instance = super().update(instance, validated_data)
        if categories is not None:
            instance.categories.set(categories)
        return instance