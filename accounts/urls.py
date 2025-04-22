from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, RegisterView, ChangeRoleView, CustomTokenObtainPairView

# Router pour les opérations CRUD sur les utilisateurs
router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')

# Routes d'authentification
auth_patterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
]

# Routes des utilisateurs
user_patterns = [
    path('', include(router.urls)),  # CRUD sur les utilisateurs
    path('<int:user_id>/role/', ChangeRoleView.as_view(), name='change-role'),
]