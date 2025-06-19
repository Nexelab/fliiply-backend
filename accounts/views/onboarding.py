from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.services.stripe_service import generate_account_link
from drf_yasg.utils import swagger_auto_schema


class StripeOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Generate Stripe Connect onboarding link for sellers",
        operation_summary="Generate Stripe Onboarding Link",
        tags=['Seller Onboarding'],
        responses={200: openapi.Response(description="Stripe Connect onboarding URL")},
    )
    def get(self, request):
        user = request.user
        url = generate_account_link(user)
        return Response({"url": url})
