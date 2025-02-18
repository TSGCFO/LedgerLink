from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    Assumes the model instance has a `user` attribute or property.
    """
    
    def has_permission(self, request, view):
        # Allow admins to access everything
        if request.user.is_staff:
            return True
        # Allow authenticated users to access list and create
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow admins to access everything
        if request.user.is_staff:
            return True
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute or property.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to modify objects.
    Anyone can read.
    """
    
    def has_permission(self, request, view):
        # Allow anyone to read
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow admins to modify
        return request.user.is_authenticated and request.user.is_staff

class HasOrganizationPermission(permissions.BasePermission):
    """
    Custom permission to handle organization-level access.
    Assumes the model instance has an `organization` attribute or property.
    """
    
    def has_permission(self, request, view):
        # Require authentication
        if not request.user.is_authenticated:
            return False
        
        # Allow admins full access
        if request.user.is_staff:
            return True
        
        # Check if user has an organization
        return hasattr(request.user, 'organization') and request.user.organization is not None
    
    def has_object_permission(self, request, view, obj):
        # Allow admins full access
        if request.user.is_staff:
            return True
        
        # Check if object and user belong to same organization
        user_org = getattr(request.user, 'organization', None)
        obj_org = getattr(obj, 'organization', None)
        
        return user_org and obj_org and user_org == obj_org

class HasAPIAccess(permissions.BasePermission):
    """
    Custom permission to check if user has API access enabled.
    Useful for controlling access to API endpoints separately from web interface.
    """
    
    def has_permission(self, request, view):
        # Require authentication
        if not request.user.is_authenticated:
            return False
        
        # Allow admins full access
        if request.user.is_staff:
            return True
        
        # Check for API access flag
        return getattr(request.user, 'has_api_access', False)

class HasModulePermission(permissions.BasePermission):
    """
    Custom permission to check if user has access to specific modules.
    Requires the view to specify which module it belongs to.
    """
    
    def has_permission(self, request, view):
        # Require authentication
        if not request.user.is_authenticated:
            return False
        
        # Allow admins full access
        if request.user.is_staff:
            return True
        
        # Get required module from view
        required_module = getattr(view, 'required_module', None)
        if not required_module:
            return False
        
        # Check user's module permissions
        return request.user.has_module_permission(required_module)

def module_required(module_name):
    """
    Decorator to specify which module a view requires access to.
    Usage:
    @module_required('orders')
    class OrderViewSet(viewsets.ModelViewSet):
        ...
    """
    def decorator(view_class):
        view_class.required_module = module_name
        return view_class
    return decorator