"""
Health check endpoints for monitoring application status.
"""
import logging
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .exceptions import APIResponse

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='get',
    operation_description="Basic application health check",
    operation_summary="Health Check",
    tags=['System Health'],
    responses={
        200: openapi.Response(
            description="Application is healthy",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Application is healthy",
                    "data": {
                        "status": "healthy",
                        "database": "connected",
                        "version": "1.0.0"
                    }
                }
            }
        ),
        503: openapi.Response(description="Service unavailable")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint.
    """
    try:
        # Check database connectivity
        connection.ensure_connection()
        
        # Basic health response
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
        }
        
        return APIResponse.success(
            data=health_data,
            message="Application is healthy"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        
        return APIResponse.error(
            error_code='health_check_failed',
            message="Application health check failed",
            details={'error': str(e)},
            status_code=503
        )


@swagger_auto_schema(
    method='get',
    operation_description="Comprehensive system health check with detailed status of all components",
    operation_summary="Detailed Health Check",
    tags=['System Health'],
    responses={
        200: openapi.Response(description="System is healthy"),
        503: openapi.Response(description="System has issues")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def detailed_health_check(request):
    """
    Detailed health check endpoint with comprehensive system status.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database check
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        overall_healthy = False
    
    # Cache check (if configured)
    try:
        cache_key = 'health_check_test'
        cache.set(cache_key, 'test_value', 30)
        cache_value = cache.get(cache_key)
        
        if cache_value == 'test_value':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'message': 'Cache is working properly'
            }
        else:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'message': 'Cache read/write test failed'
            }
            overall_healthy = False
            
    except Exception as e:
        logger.warning(f"Cache health check failed: {str(e)}")
        health_status['checks']['cache'] = {
            'status': 'warning',
            'message': f'Cache check failed (may not be configured): {str(e)}'
        }
    
    # Set overall status
    health_status['status'] = 'healthy' if overall_healthy else 'unhealthy'
    
    status_code = 200 if overall_healthy else 503
    
    return APIResponse.success(
        data=health_status,
        message="Detailed health check completed"
    ) if overall_healthy else APIResponse.error(
        error_code='health_check_failed',
        message="System is unhealthy",
        details=health_status,
        status_code=status_code
    )


@swagger_auto_schema(
    method='get',
    operation_description="Kubernetes readiness probe - checks if application is ready to serve traffic",
    operation_summary="Readiness Check",
    tags=['System Health'],
    responses={
        200: openapi.Response(description="Application is ready"),
        503: openapi.Response(description="Application is not ready")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check to determine if the application is ready to serve traffic.
    """
    try:
        # Check if we can connect to the database and perform a basic query
        from accounts.models import User
        User.objects.first()  # Simple query to verify database access
        
        return APIResponse.success(
            data={'ready': True},
            message="Application is ready to serve traffic"
        )
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}", exc_info=True)
        
        return APIResponse.error(
            error_code='not_ready',
            message="Application is not ready to serve traffic",
            details={'error': str(e)},
            status_code=503
        )


@swagger_auto_schema(
    method='get',
    operation_description="Kubernetes liveness probe - checks if application is alive and responsive",
    operation_summary="Liveness Check",
    tags=['System Health'],
    responses={
        200: openapi.Response(description="Application is alive")
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check to determine if the application is alive.
    """
    return APIResponse.success(
        data={'alive': True},
        message="Application is alive"
    )