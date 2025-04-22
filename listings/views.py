from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from .models import Listing
from .serializers import ListingSerializer
from accounts.permissions import IsSeller

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsSeller]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all listings (authenticated users only).",
        responses={200: ListingSerializer(many=True), 401: "Unauthorized"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new listing (sellers only).",
        responses={201: ListingSerializer, 403: "Forbidden", 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a listing by ID (authenticated users only).",
        responses={200: ListingSerializer, 401: "Unauthorized", 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        listing = serializer.save(seller=self.request.user)
        listing.product.price = listing.product.calculate_average_price()
        listing.product.save()

    def perform_update(self, serializer):
        listing = serializer.save()
        listing.product.price = listing.product.calculate_average_price()
        listing.product.save()