from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView
from .health import health_check, detailed_health_check, readiness_check, liveness_check

schema_view = get_schema_view(
    openapi.Info(
        title="Fliiply Trading Card Game API",
        default_version='v1',
        description="""
# Fliiply Backend API Documentation

A comprehensive API for trading card game (TCG) marketplace operations.

## Features
- **User Management**: Registration, authentication, roles (buyer/seller/verifier)
- **Product Catalog**: TCG products with variants (language, version, condition, grade)
- **Marketplace**: Listings, cart management, order processing
- **Payment**: Stripe integration for secure payments
- **Disputes**: Built-in dispute resolution system
- **Search**: Advanced search with history tracking
- **Collections**: User collections management

## Authentication
Most endpoints require JWT authentication. Use the `/api/auth/login/` endpoint to obtain tokens.

Header format: `Authorization: Bearer <your_jwt_token>`

## Error Handling
All endpoints return standardized error responses with proper HTTP status codes.
        """,
        terms_of_service="https://www.fliiply.com/terms/",
        contact=openapi.Contact(
            name="Fliiply API Support",
            email="contact@nexelab.com",
            url="https://www.fliiply.com/support"
        ),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.v1.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Health check endpoints
    path('health/', health_check, name='health-check'),
    path('health/detailed/', detailed_health_check, name='detailed-health-check'),
    path('health/ready/', readiness_check, name='readiness-check'),
    path('health/live/', liveness_check, name='liveness-check'),
]

urlpatterns += [
    path("api/stripe/onboarding/refresh/", TemplateView.as_view(template_name="stripe/refresh.html")),
    path("api/stripe/onboarding/complete/", TemplateView.as_view(template_name="stripe/return.html")),
]