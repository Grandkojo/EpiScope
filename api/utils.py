from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()


def assign_user_to_group(user, group_name):
    """
    Assign a user to a specific group.
    
    Args:
        user: User instance
        group_name: Name of the group ('Users', 'Admins')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False


def remove_user_from_group(user, group_name):
    """
    Remove a user from a specific group.
    
    Args:
        user: User instance
        group_name: Name of the group ('Users', 'Admins')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        group = Group.objects.get(name=group_name)
        user.groups.remove(group)
        return True
    except Group.DoesNotExist:
        return False


def get_user_groups(user):
    """
    Get all groups that a user belongs to.
    
    Args:
        user: User instance
    
    Returns:
        QuerySet: Groups the user belongs to
    """
    return user.groups.all()


def is_user_in_group(user, group_name):
    """
    Check if a user belongs to a specific group.
    
    Args:
        user: User instance
        group_name: Name of the group
    
    Returns:
        bool: True if user is in group, False otherwise
    """
    return user.groups.filter(name=group_name).exists()


def get_users_in_group(group_name):
    """
    Get all users in a specific group.
    
    Args:
        group_name: Name of the group
    
    Returns:
        QuerySet: Users in the group
    """
    try:
        group = Group.objects.get(name=group_name)
        return group.user_set.all()
    except Group.DoesNotExist:
        return User.objects.none()


def promote_user_to_admin(user):
    """
    Promote a user to admin status.
    
    Args:
        user: User instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user.is_admin = True
        user.save()
        assign_user_to_group(user, 'Admins')
        return True
    except Exception:
        return False


def demote_admin_to_user(user):
    """
    Demote an admin to regular user status.
    
    Args:
        user: User instance
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user.is_admin = False
        user.save()
        remove_user_from_group(user, 'Admins')
        assign_user_to_group(user, 'Users')
        return True
    except Exception:
        return False


def get_user_permission_summary(user):
    """
    Get a summary of user permissions and groups.
    
    Args:
        user: User instance
    
    Returns:
        dict: Summary of user permissions
    """
    groups = get_user_groups(user)
    permissions = user.get_all_permissions()
    
    return {
        'username': user.username,
        'email': user.email,
        'is_superuser': user.is_superuser,
        'is_admin': user.is_admin,
        'is_staff': user.is_staff,
        'groups': [group.name for group in groups],
        'permissions': list(permissions),
        'total_permissions': len(permissions)
    }


def create_default_user_groups():
    """
    Create default user groups if they don't exist.
    
    Returns:
        dict: Status of group creation
    """
    groups_created = {}
    
    # Create Users group
    users_group, created = Group.objects.get_or_create(name='Users')
    groups_created['Users'] = created
    
    # Create Admins group
    admins_group, created = Group.objects.get_or_create(name='Admins')
    groups_created['Admins'] = created
    
    return groups_created 

# Rate Limiting Utilities
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework.response import Response
from rest_framework import status
import time
import hashlib

class CustomUserRateThrottle(UserRateThrottle):
    """
    Custom user rate throttle with more granular control
    """
    rate = '2000/hour'  # Increased from 1000/hour
    scope = 'user'
    
    def get_cache_key(self, request, view):
        """
        Generate cache key based on user ID and IP
        """
        if request.user.is_authenticated:
            ident = f"{request.user.id}_{request.META.get('REMOTE_ADDR', '')}"
        else:
            ident = request.META.get('REMOTE_ADDR', '')
        
        return f"throttle_{self.scope}_{ident}"

class SensitiveEndpointThrottle(ScopedRateThrottle):
    """
    Throttle for sensitive endpoints (login, password reset, etc.)
    """
    scope = 'sensitive'
    rate = '1010/minute'  # Increased from 10/minute

class APIRateThrottle(ScopedRateThrottle):
    """
    General API rate throttle
    """
    scope = 'api'
    rate = '2000/hour'  # Increased from 1000/hour

class BurstRateThrottle(ScopedRateThrottle):
    """
    Burst rate throttle for high-frequency endpoints
    """
    scope = 'burst'
    rate = '560/minute'  # Increased from 60/minute

def rate_limit_by_ip(limit=1100, period=3600):  # Increased from 100
    """
    Decorator for rate limiting by IP address
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Create cache key
            cache_key = f"rate_limit_{ip}_{view_func.__name__}"
            
            # Check current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                response = HttpResponse(
                    f"Rate limit exceeded. Maximum {limit} requests per {period} seconds.",
                    status=429
                )
                return response
            
            # Increment count
            cache.set(cache_key, current_count + 1, period)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def rate_limit_by_user(limit=2000, period=3600):  # Increased from 1000
    """
    Decorator for rate limiting by authenticated user
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # Create cache key based on user ID
            cache_key = f"rate_limit_user_{request.user.id}_{view_func.__name__}"
            
            # Check current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                response = HttpResponse(
                    f"Rate limit exceeded. Maximum {limit} requests per {period} seconds.",
                    status=429
                )
                return response
            
            # Increment count
            cache.set(cache_key, current_count + 1, period)
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def get_rate_limit_info(request, throttle_class):
    """
    Get rate limit information for debugging
    """
    throttle = throttle_class()
    throttle.request = request
    throttle.view = None
    
    cache_key = throttle.get_cache_key(request, None)
    history = cache.get(cache_key, [])
    
    now = time.time()
    while history and history[-1] <= now - throttle.duration:
        history.pop()
    
    return {
        'limit': throttle.num_requests,
        'remaining': max(0, throttle.num_requests - len(history)),
        'reset_time': now + throttle.duration if history else now,
        'cache_key': cache_key
    } 