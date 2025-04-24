from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OfferViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]