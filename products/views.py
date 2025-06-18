from rest_framework import viewsets
from accounts.permissions import IsPremiumUser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
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
    permission_classes = [IsAuthenticated, IsPremiumUser]

    def get_queryset(self):
        # Ne renvoie rien pour la génération Swagger ou utilisateur anonyme
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Collection.objects.none()

        return Collection.objects.filter(user=self.request.user).prefetch_related('variants')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
