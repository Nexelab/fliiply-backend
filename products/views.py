from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from accounts.permissions import IsPremiumUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
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
    SearchHistory,
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
    SearchHistorySerializer,
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.select_related('parent').all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(operation_description="List all categories.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Create a new category.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve a category.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
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

    @swagger_auto_schema(operation_description="List all products.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Create a new product.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Retrieve a product.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Add an image to a product.",
        request_body=ProductImageSerializer,
        responses={201: ProductImageSerializer}
    )
    @action(detail=True, methods=['post'], url_path='add-image')
    def add_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    @swagger_auto_schema(operation_description="List all languages.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer

    @swagger_auto_schema(operation_description="List all versions.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer

    @swagger_auto_schema(operation_description="List all conditions.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    @swagger_auto_schema(operation_description="List all grades.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class VariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

    @swagger_auto_schema(operation_description="List all product variants.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    @swagger_auto_schema(operation_description="List all listings.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ne renvoie rien pour la génération Swagger ou utilisateur anonyme
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Collection.objects.none()

        return Collection.objects.filter(user=self.request.user).prefetch_related('variants')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SearchSuggestionView(APIView):
    """Return search suggestions for product fields and optional history."""

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
                SearchHistory = apps.get_model("products", "SearchHistory")
            except LookupError:
                SearchHistory = None

            if SearchHistory is not None:
                history_terms = (
                    SearchHistory.objects.filter(term__icontains=query)
                    .values_list("term", flat=True)
                    .distinct()[:5]
                )
                suggestions.update(history_terms)

        return Response(sorted(suggestions))

class SearchView(generics.ListAPIView):
    serializer_class = ListingSerializer
    pagination_class = PageNumberPagination

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
            params = request.query_params.dict()
            query = params.pop('q', '')
            params.pop('page', None)

            SearchHistory.objects.create(
                user=request.user,
                query=query,
                filters=params or None,
            )

            histories = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
            if histories.count() > 50:
                for history in histories[50:]:
                    history.delete()

        return response
