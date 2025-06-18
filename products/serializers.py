from rest_framework import serializers
from .models import (
    Category,
    Language,
    Version,
    Condition,
    Grade,
    Product,
    ProductImage,
    Variant,
    Listing,
    Collection,
    CollectionItem,
)

# --- Base Serializers ---

class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True, required=False)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children']
        read_only_fields = ['slug', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'name']

class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ['id', 'code', 'name', 'tcg_types', 'description', 'displayable']

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ['id', 'code', 'label', 'is_graded']

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'value', 'grader']

# --- Product and Related ---

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'created_at']
        read_only_fields = ['created_at']

class VariantSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(read_only=True)
    version = VersionSerializer(read_only=True)
    condition = ConditionSerializer(read_only=True)
    grade = GradeSerializer(read_only=True)

    language_id = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), write_only=True, source='language'
    )
    version_id = serializers.PrimaryKeyRelatedField(
        queryset=Version.objects.all(), write_only=True, source='version'
    )
    condition_id = serializers.PrimaryKeyRelatedField(
        queryset=Condition.objects.all(), write_only=True, source='condition'
    )
    grade_id = serializers.PrimaryKeyRelatedField(
        queryset=Grade.objects.all(), write_only=True, allow_null=True, required=False, source='grade'
    )

    class Meta:
        model = Variant
        fields = [
            'id', 'product',
            'language', 'version', 'condition', 'grade',
            'language_id', 'version_id', 'condition_id', 'grade_id'
        ]


class ProductSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    categories_ids = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, write_only=True, source='categories')
    allowed_languages = LanguageSerializer(many=True, read_only=True)
    allowed_languages_ids = serializers.PrimaryKeyRelatedField(queryset=Language.objects.all(), many=True, write_only=True, source='allowed_languages')
    allowed_versions = VersionSerializer(many=True, read_only=True)
    allowed_versions_ids = serializers.PrimaryKeyRelatedField(queryset=Version.objects.all(), many=True, write_only=True, source='allowed_versions')
    images = ProductImageSerializer(many=True, read_only=True)
    average_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'block', 'series', 'description', 'tcg_type', 'slug',
            'categories', 'categories_ids',
            'allowed_languages', 'allowed_languages_ids',
            'allowed_versions', 'allowed_versions_ids',
            'images', 'average_price', 'total_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'average_price', 'total_stock']

    def get_average_price(self, obj):
        return obj.calculate_average_price()

    def get_total_stock(self, obj):
        return obj.calculate_total_stock()

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        allowed_languages = validated_data.pop('allowed_languages', [])
        allowed_versions = validated_data.pop('allowed_versions', [])
        product = Product.objects.create(**validated_data)
        product.categories.set(categories)
        product.allowed_languages.set(allowed_languages)
        product.allowed_versions.set(allowed_versions)
        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        allowed_languages = validated_data.pop('allowed_languages', None)
        allowed_versions = validated_data.pop('allowed_versions', None)
        instance = super().update(instance, validated_data)
        if categories is not None:
            instance.categories.set(categories)
        if allowed_languages is not None:
            instance.allowed_languages.set(allowed_languages)
        if allowed_versions is not None:
            instance.allowed_versions.set(allowed_versions)
        return instance

class ListingSerializer(serializers.ModelSerializer):
    variant = VariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=Variant.objects.all(), write_only=True, source='variant'
    )

    class Meta:
        model = Listing
        fields = [
            'id', 'product', 'variant', 'variant_id',
            'seller', 'price', 'stock', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CollectionItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source='product'
    )

    class Meta:
        model = CollectionItem
        fields = ['id', 'product', 'product_id', 'quantity']


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    products_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True, write_only=True, source='products'
    )

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'slug', 'description',
            'products', 'products_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        products = validated_data.pop('products', [])
        collection = Collection.objects.create(**validated_data)
        collection.products.set(products)
        return collection

    def update(self, instance, validated_data):
        products = validated_data.pop('products', None)
        instance = super().update(instance, validated_data)
        if products is not None:
            instance.products.set(products)
        return instance
