from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.services.stripe_service import generate_account_link
from drf_yasg.utils import swagger_auto_schema


class StripeOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Génère un lien d'onboarding Stripe",
        responses={200: openapi.Response(description="URL Stripe Connect onboarding")},
    )
    def get(self, request):
        user = request.user
        url = generate_account_link(user)
        return Response({"url": url})
