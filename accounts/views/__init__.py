# views/__init__.py

from .main import (
    UserViewSet,
    RegisterView,
    ChangeRoleView,
    CustomTokenObtainPairView,
    AddressViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    VerifyEmailView,
    ResendVerificationEmailView,
    VerifyKYCView,
)

from .onboarding import StripeOnboardingView
from .main import StripeSetupIntentView, StripeSubscriptionView
from .webhook import stripe_webhook
