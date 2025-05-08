from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, RegisterView, ChangeRoleView, CustomTokenObtainPairView, AddressViewSet, \
    PasswordResetRequestView, PasswordResetConfirmView, VerifyEmailView, ResendVerificationEmailView

# Router pour les opérations CRUD sur les utilisateurs
router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')
router.register(r'addresses', AddressViewSet, basename='addresses')

# Routes d'authentification
auth_patterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset_confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('verify_email/', VerifyEmailView.as_view(), name='verify_email'),
    path('resend_verification_email/', ResendVerificationEmailView.as_view(), name='resend_verification_email'),

]

# Routes des utilisateurs
user_patterns = [
    path('', include(router.urls)),  # CRUD sur les utilisateurs
    path('<int:user_id>/role/', ChangeRoleView.as_view(), name='change-role'),
]