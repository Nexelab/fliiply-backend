"""
Custom mixins for consistent API behavior.
"""
from rest_framework import status
from rest_framework.response import Response
from .exceptions import APIResponse


class StandardResponseMixin:
    """
    Mixin to provide standard response formatting for ViewSets.
    """
    
    def create(self, request, *args, **kwargs):
        """Override create to use standard response format."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return APIResponse.created(
            data=serializer.data,
            message=f"{self.get_object_name()} created successfully"
        )
    
    def update(self, request, *args, **kwargs):
        """Override update to use standard response format."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.get_object_name()} updated successfully"
        )
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to use standard response format."""
        instance = self.get_object()
        self.perform_destroy(instance)
        
        return APIResponse.no_content(
            message=f"{self.get_object_name()} deleted successfully"
        )
    
    def list(self, request, *args, **kwargs):
        """Override list to use standard response format."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Wrap paginated response in standard format
            return APIResponse.success(
                data=paginated_response.data['results'],
                message=f"{self.get_object_name()} list retrieved successfully",
                meta={
                    'pagination': {
                        'count': paginated_response.data['count'],
                        'next': paginated_response.data['next'],
                        'previous': paginated_response.data['previous'],
                    }
                }
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.get_object_name()} list retrieved successfully"
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use standard response format."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message=f"{self.get_object_name()} retrieved successfully"
        )
    
    def get_object_name(self):
        """Get a human-readable name for the object."""
        if hasattr(self, 'object_name'):
            return self.object_name
        
        model_name = getattr(self.get_queryset().model, '__name__', 'Object')
        return model_name.lower()


class ValidationMixin:
    """
    Mixin to provide enhanced validation with better error messages.
    """
    
    def validate_serializer(self, serializer_class, data, instance=None, partial=False):
        """
        Validate data with a serializer and return formatted errors if invalid.
        """
        serializer = serializer_class(instance=instance, data=data, partial=partial)
        
        if not serializer.is_valid():
            # Format validation errors
            formatted_errors = {}
            for field, errors in serializer.errors.items():
                if isinstance(errors, list):
                    formatted_errors[field] = [str(error) for error in errors]
                else:
                    formatted_errors[field] = str(errors)
            
            return None, formatted_errors
        
        return serializer, None
    
    def validate_required_fields(self, data, required_fields):
        """
        Validate that required fields are present in the data.
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'missing_fields': missing_fields,
                'message': f"Required fields missing: {', '.join(missing_fields)}"
            }
        
        return None


class PermissionMixin:
    """
    Mixin to provide enhanced permission checking.
    """
    
    def check_object_permission(self, request, obj, permission_check):
        """
        Check if user has permission for a specific object.
        """
        if not permission_check(request.user, obj):
            return APIResponse.forbidden(
                message="You don't have permission to access this resource"
            )
        return None
    
    def check_ownership(self, request, obj, owner_field='user'):
        """
        Check if the current user owns the object.
        """
        owner = getattr(obj, owner_field, None)
        if owner != request.user:
            return APIResponse.forbidden(
                message="You can only access your own resources"
            )
        return None


class BusinessLogicMixin:
    """
    Mixin to provide common business logic validation.
    """
    
    def validate_business_rule(self, condition, error_message, error_code='business_rule_violation'):
        """
        Validate a business rule and return error response if violated.
        """
        if not condition:
            return APIResponse.bad_request(
                message=error_message,
                details={'error_code': error_code}
            )
        return None
    
    def check_resource_availability(self, resource, field='stock', required_amount=1):
        """
        Check if a resource has sufficient availability.
        """
        available = getattr(resource, field, 0)
        if available < required_amount:
            return APIResponse.bad_request(
                message=f"Insufficient {field}. Available: {available}, Required: {required_amount}",
                details={
                    'available': available,
                    'required': required_amount,
                    'field': field
                }
            )
        return None