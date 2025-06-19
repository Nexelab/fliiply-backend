from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from accounts.permissions import IsPremiumUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from core.mixins import StandardResponseMixin, ValidationMixin, PermissionMixin
from core.exceptions import APIResponse
from .models import (
    Product,
    Category,
    ProductImage,
    Language,
    Version,
    Condition,
    Grade,
    Variant,
    Listing,
    Collection,
)
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductImageSerializer,
    LanguageSerializer,
    VersionSerializer,
    ConditionSerializer,
    GradeSerializer,
    VariantSerializer,
    ListingSerializer,
    CollectionSerializer,
)

class CategoryViewSet(StandardResponseMixin, ValidationMixin, PermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    
    Categories are used to organize products in a hierarchical structure.
    Only administrators can create, update or delete categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    object_name = "category"

    def get_queryset(self):
        return Category.objects.select_related('parent').all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all product categories with hierarchical structure",
        operation_summary="List Categories",
        tags=['Product Catalog'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new product category (Admin only)",
        operation_summary="Create Category",
        tags=['Product Catalog'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific category",
        operation_summary="Get Category",
        tags=['Product Catalog'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a category (Admin only)",
        operation_summary="Update Category",
        tags=['Product Catalog'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a category (Admin only)",
        operation_summary="Delete Category",
        tags=['Product Catalog'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing TCG products.
    
    Products represent individual trading cards or TCG items with their basic information.
    Products can have multiple variants based on language, version, condition, and grade.
    Only administrators can create, update or delete products.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.prefetch_related('categories', 'images').all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_image']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all TCG products with their basic information",
        operation_summary="List Products", 
        tags=['Product Catalog'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new TCG product (Admin only)",
        operation_summary="Create Product",
        tags=['Product Catalog'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific product including variants and images",
        operation_summary="Get Product",
        tags=['Product Catalog'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a product (Admin only)",
        operation_summary="Update Product",
        tags=['Product Catalog'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a product (Admin only)",
        operation_summary="Delete Product", 
        tags=['Product Catalog'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Add an image to a product (Admin only)",
        operation_summary="Add Product Image",
        tags=['Product Catalog'],
        request_body=ProductImageSerializer,
        responses={201: ProductImageSerializer}
    )
    @action(detail=True, methods=['post'], url_path='add-image')
    def add_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return APIResponse.created(serializer.data, "Image added successfully")
        return APIResponse.validation_error(serializer.errors)

class LanguageViewSet(viewsets.ModelViewSet):
    """Language options for TCG products (e.g., English, French, Japanese)."""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    @swagger_auto_schema(
        operation_description="List all available languages for TCG products",
        operation_summary="List Languages",
        tags=['Product Attributes']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class VersionViewSet(viewsets.ModelViewSet):
    """Version options for TCG products (e.g., First Edition, Unlimited)."""
    queryset = Version.objects.all()
    serializer_class = VersionSerializer

    @swagger_auto_schema(
        operation_description="List all available versions for TCG products",
        operation_summary="List Versions",
        tags=['Product Attributes']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ConditionViewSet(viewsets.ModelViewSet):
    """Condition options for TCG products (e.g., Near Mint, Played)."""
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    @swagger_auto_schema(
        operation_description="List all available conditions for TCG products",
        operation_summary="List Conditions",
        tags=['Product Attributes']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class GradeViewSet(viewsets.ModelViewSet):
    """Professional grading options (e.g., PSA 10, BGS 9.5)."""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    @swagger_auto_schema(
        operation_description="List all available professional grades",
        operation_summary="List Grades",
        tags=['Product Attributes']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class VariantViewSet(viewsets.ModelViewSet):
    """Product variants combining language, version, condition, and grade."""
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

    @swagger_auto_schema(
        operation_description="List all product variants with their specific attributes",
        operation_summary="List Product Variants",
        tags=['Product Catalog']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ListingViewSet(viewsets.ModelViewSet):
    """Marketplace listings where sellers offer their products for sale."""
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    @swagger_auto_schema(
        operation_description="List all marketplace listings with pricing and availability",
        operation_summary="List Marketplace Listings",
        tags=['Marketplace']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CollectionViewSet(viewsets.ModelViewSet):
    """
    User collections for organizing owned or wanted TCG products.
    
    Collections allow users to organize their card collections and track ownership.
    Users can only access their own collections.
    """
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ne renvoie rien pour la génération Swagger ou utilisateur anonyme
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Collection.objects.none()

        return Collection.objects.filter(user=self.request.user).prefetch_related('variants')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="List user's collections",
        operation_summary="List My Collections",
        tags=['Collections']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new collection",
        operation_summary="Create Collection",
        tags=['Collections']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get collection details",
        operation_summary="Get Collection",
        tags=['Collections']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class SearchSuggestionView(APIView):
    """
    Search suggestions API providing auto-complete functionality.
    
    Returns suggestions based on product names, series, blocks, and user search history.
    """

    @swagger_auto_schema(
        operation_description="Get search suggestions based on partial query",
        operation_summary="Search Suggestions",
        tags=['Search & Discovery'],
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Partial search query",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="List of search suggestions",
                examples={
                    "application/json": [
                        "Charizard",
                        "Charizard Base Set",
                        "Base Set"
                    ]
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", "").strip()
        suggestions: set[str] = set()

        if query:
            suggestions.update(
                Product.objects.filter(name__icontains=query)
                .values_list("name", flat=True)
                .distinct()
            )
            suggestions.update(
                Product.objects.filter(series__icontains=query)
                .exclude(series__isnull=True)
                .values_list("series", flat=True)
                .distinct()
            )
            suggestions.update(
                Product.objects.filter(block__icontains=query)
                .exclude(block__isnull=True)
                .values_list("block", flat=True)
                .distinct()
            )

            # Include terms from SearchHistory model if it exists
            from django.apps import apps

            try:
                SearchHistory = apps.get_model("searches", "SearchHistory")
            except LookupError:
                SearchHistory = None

            if SearchHistory is not None:
                history_terms = (
                    SearchHistory.objects.filter(query__icontains=query)
                    .values_list("query", flat=True)
                    .distinct()[:5]
                )
                suggestions.update(history_terms)

        return Response(sorted(suggestions))

class SearchView(generics.ListAPIView):
    """
    Advanced search API for finding marketplace listings.
    
    Supports filtering by multiple criteria including product attributes,
    price range, condition, and availability. Automatically saves search
    history for authenticated users.
    """
    serializer_class = ListingSerializer
    pagination_class = PageNumberPagination

    @swagger_auto_schema(
        operation_description="Search marketplace listings with advanced filters",
        operation_summary="Search Listings",
        tags=['Search & Discovery'],
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('tcg_type', openapi.IN_QUERY, description="TCG Type (pokemon, yugioh, magic)", type=openapi.TYPE_STRING),
            openapi.Parameter('block', openapi.IN_QUERY, description="Product block", type=openapi.TYPE_STRING),
            openapi.Parameter('series', openapi.IN_QUERY, description="Product series", type=openapi.TYPE_STRING),
            openapi.Parameter('language', openapi.IN_QUERY, description="Language code", type=openapi.TYPE_STRING),
            openapi.Parameter('version', openapi.IN_QUERY, description="Version code", type=openapi.TYPE_STRING),
            openapi.Parameter('condition', openapi.IN_QUERY, description="Condition code", type=openapi.TYPE_STRING),
            openapi.Parameter('grade', openapi.IN_QUERY, description="Grade value", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('availability', openapi.IN_QUERY, description="in_stock or out_of_stock", type=openapi.TYPE_STRING),
        ]
    )

    def get_queryset(self):
        qs = Listing.objects.filter(status='active').select_related(
            'product',
            'variant__language',
            'variant__version',
            'variant__condition',
            'variant__grade',
        )

        query = self.request.query_params.get('q')
        if query:
            qs = qs.filter(
                Q(product__name__icontains=query)
                | Q(product__series__icontains=query)
                | Q(product__block__icontains=query)
                | Q(variant__language__name__icontains=query)
                | Q(variant__version__name__icontains=query)
                | Q(variant__condition__label__icontains=query)
                | Q(variant__grade__grader__icontains=query)
                | Q(variant__grade__value__icontains=query)
            )

        filters = self.request.query_params
        if 'tcg_type' in filters:
            qs = qs.filter(product__tcg_type=filters['tcg_type'])
        if 'block' in filters:
            qs = qs.filter(product__block__iexact=filters['block'])
        if 'series' in filters:
            qs = qs.filter(product__series__iexact=filters['series'])
        if 'language' in filters:
            qs = qs.filter(variant__language__code=filters['language'])
        if 'version' in filters:
            qs = qs.filter(variant__version__code=filters['version'])
        if 'condition' in filters:
            qs = qs.filter(variant__condition__code=filters['condition'])
        if 'grade' in filters:
            qs = qs.filter(variant__grade__grader=filters['grade'])
        if 'min_price' in filters:
            qs = qs.filter(price__gte=filters['min_price'])
        if 'max_price' in filters:
            qs = qs.filter(price__lte=filters['max_price'])
        if filters.get('availability') == 'in_stock':
            qs = qs.filter(stock__gt=0)
        if filters.get('availability') == 'out_of_stock':
            qs = qs.filter(stock=0)

        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        if request.user.is_authenticated:
            from django.apps import apps
            try:
                SearchHistory = apps.get_model("searches", "SearchHistory")
                params = request.query_params.dict()
                query = params.pop('q', '')
                params.pop('page', None)

                SearchHistory.objects.create(
                    user=request.user,
                    query=query,
                )

                histories = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
                if histories.count() > 50:
                    for history in histories[50:]:
                        history.delete()
            except LookupError:
                pass  # SearchHistory model not available

        return response
