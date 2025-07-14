from rest_framework import permissions
from django.contrib.auth.models import Group


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


class IsSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow superusers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to all users,
    but write access only to admin users.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to all users,
    but write access only to superusers.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to superusers
        return request.user.is_authenticated and request.user.is_superuser


class DiseaseDataPermission(permissions.BasePermission):
    """
    Permission for disease data access:
    - All authenticated users can view
    - Only superusers can modify
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_superuser


class DiseaseManagementPermission(permissions.BasePermission):
    """
    Permission for disease management:
    - All authenticated users can view
    - Admins and superusers can modify
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


class UserManagementPermission(permissions.BasePermission):
    """
    Permission for user management:
    - Users can view and update their own profile
    - Admins can view all users
    - Superusers can do everything
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can view and update their own profile
        if obj == request.user:
            return True
        
        # Admins can view other users but not modify them
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_admin or request.user.is_superuser
        
        # Only superusers can modify other users
        return request.user.is_superuser


class DashboardPermission(permissions.BasePermission):
    """
    Permission for dashboard access:
    - All authenticated users can access dashboard data
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class HotspotsPermission(permissions.BasePermission):
    """
    Permission for national hotspots access:
    - All authenticated users can view hotspots data
    - Only superusers can modify
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_superuser 