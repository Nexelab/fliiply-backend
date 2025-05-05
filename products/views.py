from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import Product, Category, ProductImage
from .serializers import ProductSerializer, CategorySerializer, ProductImageSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.select_related('parent').all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all categories (authenticated users only).",
        responses={200: CategorySerializer(many=True), 401: "Unauthorized"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new category (admin only).",
        responses={201: CategorySerializer, 403: "Forbidden", 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a category by ID (authenticated users only).",
        responses={200: CategorySerializer, 401: "Unauthorized", 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.prefetch_related('categories', 'images', 'price_histories').all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_image']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all products (authenticated users only).",
        responses={200: ProductSerializer(many=True), 401: "Unauthorized"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new product (admin only).",
        responses={201: ProductSerializer, 403: "Forbidden", 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a product by ID (authenticated users only).",
        responses={200: ProductSerializer, 401: "Unauthorized", 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Add an image to a product (admin only).",
        request_body=ProductImageSerializer,
        responses={201: ProductImageSerializer, 400: "Bad Request", 403: "Forbidden", 404: "Not Found"}
    )
    @action(detail=True, methods=['post'], url_path='add-image')
    def add_image(self, request, pk=None):
        product = self.get_object()
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)