from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from products.models import Product
from products.serializers import ProductSerializer

from .models import SearchHistory


class SearchView(APIView):
    """
    Product search with automatic history tracking.
    
    Searches products by name and automatically saves search history
    for authenticated users. Maintains up to 50 recent searches per user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Search products by name and save search history",
        operation_summary="Search Products",
        tags=['Search & Discovery'],
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Search query for product names",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ProductSerializer(many=True),
            401: "Unauthorized"
        }
    )
    def get(self, request):
        query = request.query_params.get('q', '')
        products = Product.objects.filter(name__icontains=query)
        serialized = ProductSerializer(products, many=True)

        if query:
            SearchHistory.objects.create(user=request.user, query=query)
            histories = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')
            if histories.count() >= 50:
                histories[50:].delete()

        return Response(serialized.data)
