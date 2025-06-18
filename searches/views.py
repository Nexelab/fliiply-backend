from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from products.serializers import ProductSerializer

from .models import SearchHistory


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

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
