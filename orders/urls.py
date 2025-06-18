from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartItemViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]
