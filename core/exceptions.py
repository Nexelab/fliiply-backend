"""
Global exception handlers for consistent error responses.
"""
import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
    AuthenticationFailed,
    NotFound,
    MethodNotAllowed,
    Throttled,
)
from django.utils import timezone

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Get request info for logging
    request = context.get('request')
    user = getattr(request, 'user', None)
    user_id = getattr(user, 'id', None) if user and hasattr(user, 'id') else None
    
    # Base error response structure
    error_response = {
        'success': False,
        'timestamp': timezone.now().isoformat(),
        'path': getattr(request, 'path', '') if request else '',
        'method': getattr(request, 'method', '') if request else '',
    }
    
    if response is not None:
        # Handle DRF exceptions
        custom_response_data = error_response.copy()
        
        if isinstance(exc, ValidationError):
            custom_response_data.update({
                'error': 'validation_error',
                'message': 'Validation failed',
                'details': response.data,
                'status_code': status.HTTP_400_BAD_REQUEST
            })
            
        elif isinstance(exc, NotAuthenticated):
            custom_response_data.update({
                'error': 'authentication_required',
                'message': 'Authentication credentials required',
                'status_code': status.HTTP_401_UNAUTHORIZED
            })
            
        elif isinstance(exc, AuthenticationFailed):
            custom_response_data.update({
                'error': 'authentication_failed',
                'message': 'Invalid authentication credentials',
                'status_code': status.HTTP_401_UNAUTHORIZED
            })
            
        elif isinstance(exc, PermissionDenied):
            custom_response_data.update({
                'error': 'permission_denied',
                'message': 'You do not have permission to perform this action',
                'status_code': status.HTTP_403_FORBIDDEN
            })
            
        elif isinstance(exc, NotFound):
            custom_response_data.update({
                'error': 'not_found',
                'message': 'The requested resource was not found',
                'status_code': status.HTTP_404_NOT_FOUND
            })
            
        elif isinstance(exc, MethodNotAllowed):
            custom_response_data.update({
                'error': 'method_not_allowed',
                'message': f'Method {request.method} not allowed for this endpoint',
                'status_code': status.HTTP_405_METHOD_NOT_ALLOWED
            })
            
        elif isinstance(exc, Throttled):
            custom_response_data.update({
                'error': 'rate_limit_exceeded',
                'message': 'Rate limit exceeded. Please try again later.',
                'retry_after': getattr(exc, 'retry_after', None),
                'status_code': status.HTTP_429_TOO_MANY_REQUESTS
            })
            
        else:
            # Generic DRF exception
            custom_response_data.update({
                'error': 'api_error',
                'message': str(exc),
                'details': response.data,
                'status_code': response.status_code
            })
        
        # Log the error
        logger.warning(
            f"API Error: {exc.__class__.__name__} for user {user_id} on {request.method} {request.path}",
            extra={
                'user_id': user_id,
                'exception': exc.__class__.__name__,
                'status_code': response.status_code,
                'path': request.path,
                'method': request.method,
            }
        )
        
        response.data = custom_response_data
        return response
    
    # Handle non-DRF exceptions
    custom_response_data = error_response.copy()
    
    if isinstance(exc, Http404):
        custom_response_data.update({
            'error': 'not_found',
            'message': 'The requested resource was not found',
            'status_code': status.HTTP_404_NOT_FOUND
        })
        response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
        
    elif isinstance(exc, DjangoValidationError):
        custom_response_data.update({
            'error': 'validation_error',
            'message': 'Validation failed',
            'details': exc.message_dict if hasattr(exc, 'message_dict') else [str(exc)],
            'status_code': status.HTTP_400_BAD_REQUEST
        })
        response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        # Unhandled exception - log as error and return generic 500
        logger.error(
            f"Unhandled Exception: {exc.__class__.__name__} for user {user_id} on {request.method if request else 'Unknown'} {request.path if request else 'Unknown'}",
            exc_info=True,
            extra={
                'user_id': user_id,
                'exception': exc.__class__.__name__,
                'path': getattr(request, 'path', 'Unknown') if request else 'Unknown',
                'method': getattr(request, 'method', 'Unknown') if request else 'Unknown',
            }
        )
        
        custom_response_data.update({
            'error': 'internal_server_error',
            'message': 'An internal server error occurred',
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
        })
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


class APIResponse:
    """
    Helper class for creating consistent API responses.
    """
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
        """Create a successful response."""
        response_data = {
            'success': True,
            'message': message,
            'timestamp': timezone.now().isoformat(),
        }
        
        if data is not None:
            response_data['data'] = data
            
        if meta is not None:
            response_data['meta'] = meta
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Create an error response."""
        response_data = {
            'success': False,
            'error': error_code,
            'message': message,
            'timestamp': timezone.now().isoformat(),
            'status_code': status_code,
        }
        
        if details is not None:
            response_data['details'] = details
            
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(data=None, message="Resource created successfully"):
        """Create a 201 Created response."""
        return APIResponse.success(data, message, status.HTTP_201_CREATED)
    
    @staticmethod
    def no_content(message="Operation completed successfully"):
        """Create a 204 No Content response."""
        return APIResponse.success(None, message, status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def bad_request(message="Bad request", details=None):
        """Create a 400 Bad Request response."""
        return APIResponse.error('bad_request', message, details, status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def unauthorized(message="Authentication required"):
        """Create a 401 Unauthorized response."""
        return APIResponse.error('unauthorized', message, status_code=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="Access forbidden"):
        """Create a 403 Forbidden response."""
        return APIResponse.error('forbidden', message, status_code=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message="Resource not found"):
        """Create a 404 Not Found response."""
        return APIResponse.error('not_found', message, status_code=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def conflict(message="Resource conflict", details=None):
        """Create a 409 Conflict response."""
        return APIResponse.error('conflict', message, details, status.HTTP_409_CONFLICT)
    
    @staticmethod
    def validation_error(details, message="Validation failed"):
        """Create a validation error response."""
        return APIResponse.error('validation_error', message, details, status.HTTP_400_BAD_REQUEST)