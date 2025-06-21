# views/__init__.py

from .main import (
    UserViewSet,
    RegisterView,
    ChangeRoleView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    AddressViewSet,
    PasswordResetRequestView,
    PasswordResetVerifyView,
    PasswordResetConfirmView,
    VerifyEmailView,
    ResendVerificationEmailView,
    VerifyKYCView,
    ProfessionalInfoViewSet,
)

from .onboarding import StripeOnboardingView
from .main import StripeSetupIntentView, StripeSubscriptionView
from .webhook import stripe_webhook

