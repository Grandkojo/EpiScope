import time
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import hashlib
import json

class RateLimitMiddleware:
    """
    Custom middleware for advanced rate limiting
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if rate limiting is globally disabled
        if not getattr(settings, 'RATE_LIMITING_ENABLED', True):
            return self.get_response(request)
        
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limit(request):
            return self.get_response(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(request, client_id):
            return self._rate_limit_exceeded_response(request)
        
        response = self.get_response(request)
        
        # Add rate limit headers to response
        self._add_rate_limit_headers(response, request, client_id)
        
        return response
    
    def _should_skip_rate_limit(self, request):
        """Skip rate limiting for certain paths"""
        skip_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/health/',
            '/api/auth/user/login/',  # Skip rate limiting for login
            '/api/auth/user/register/',  # Skip rate limiting for register
        ]
        
        path = request.path
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    def _get_client_id(self, request):
        """Get unique client identifier"""
        # Try to get real IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Include user ID if authenticated
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        
        return f"{ip}_{user_id}"
    
    def _check_rate_limit(self, request, client_id):
        """Check if request is within rate limit"""
        # Different limits for different types of requests
        limits = self._get_rate_limits(request)
        
        for limit_type, (max_requests, window) in limits.items():
            cache_key = f"rate_limit_{limit_type}_{client_id}"
            
            # Get current request count
            requests = cache.get(cache_key, [])
            now = time.time()
            
            # Remove old requests outside the window
            requests = [req_time for req_time in requests if now - req_time < window]
            
            # Check if limit exceeded
            if len(requests) >= max_requests:
                return False
            
            # Add current request
            requests.append(now)
            cache.set(cache_key, requests, window)
        
        return True
    
    def _get_rate_limits(self, request):
        """Get rate limits based on request type"""
        path = request.path
        method = request.method
        
        # Default limits
        limits = {
            'general': (100, 3600),  # 100 requests per hour
        }
        
        # Stricter limits for sensitive endpoints (excluding login and register)
        if (any(sensitive in path for sensitive in ['/api/auth/', '/api/register/', '/api/password/']) and
            not any(excluded in path for excluded in ['/api/auth/user/login/', '/api/auth/user/register/'])):
            limits['sensitive'] = (10, 3600)  # 10 requests per hour
        
        # Stricter limits for AI/ML endpoints
        if any(ai_endpoint in path for ai_endpoint in ['/api/ai/', '/api/predict/', '/api/forecast/']):
            limits['ai'] = (30, 3600)  # 30 requests per hour
        
        # Stricter limits for POST requests
        if method == 'POST':
            limits['post'] = (50, 3600)  # 50 POST requests per hour
        
        return limits
    
    def _rate_limit_exceeded_response(self, request):
        """Return rate limit exceeded response"""
        return JsonResponse({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': 1800  # Retry after 30 minutes
        }, status=429)
    
    def _add_rate_limit_headers(self, response, request, client_id):
        """Add rate limit headers to response"""
        # This is a simplified version - you can enhance it based on your needs
        response['X-RateLimit-Limit'] = '100'
        response['X-RateLimit-Remaining'] = '99'  # You'd calculate this dynamically
        response['X-RateLimit-Reset'] = str(int(time.time() + 3600))

class IPWhitelistMiddleware:
    """
    Middleware to whitelist certain IP addresses from rate limiting
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Add your whitelisted IPs here
        self.whitelisted_ips = getattr(settings, 'RATE_LIMIT_WHITELIST', [])
    
    def __call__(self, request):
        # Check if IP is whitelisted
        client_ip = self._get_client_ip(request)
        if client_ip in self.whitelisted_ips:
            # Add a flag to skip rate limiting
            request.skip_rate_limit = True
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown') 