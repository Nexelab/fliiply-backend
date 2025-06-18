from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    LanguageViewSet,
    VersionViewSet,
    ConditionViewSet,
    GradeViewSet,
    VariantViewSet,
    ListingViewSet,
    CollectionViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'versions', VersionViewSet, basename='version')
router.register(r'conditions', ConditionViewSet, basename='condition')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'variants', VariantViewSet, basename='variant')
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'collections', CollectionViewSet, basename='collection')

urlpatterns = [
    path('', include(router.urls)),
]
