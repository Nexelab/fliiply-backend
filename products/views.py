from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
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