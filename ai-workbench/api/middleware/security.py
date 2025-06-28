"""Security middleware for FastAPI application."""
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
import time
import re
import logging
from typing import Optional, List, Pattern, Dict, Any, Callable, Awaitable

logger = logging.getLogger('security')

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(
        self,
        app: ASGIApp,
        enable_csp: bool = True,
        enable_hsts: bool = True,
        enable_xss: bool = True,
        enable_nosniff: bool = True,
        enable_frame_options: bool = True,
        enable_referrer_policy: bool = True,
        enable_feature_policy: bool = True,
        enable_expect_ct: bool = False,  # Certificate Transparency
        enable_permissions_policy: bool = True,  # Replaces Feature-Policy
        csp_directives: Optional[Dict[str, List[str]]] = None,
        feature_policy_directives: Optional[Dict[str, List[str]]] = None,
        permissions_policy_directives: Optional[Dict[str, List[str]]] = None,
    ):
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_hsts = enable_hsts
        self.enable_xss = enable_xss
        self.enable_nosniff = enable_nosniff
        self.enable_frame_options = enable_frame_options
        self.enable_referrer_policy = enable_referrer_policy
        self.enable_feature_policy = enable_feature_policy
        self.enable_expect_ct = enable_expect_ct
        self.enable_permissions_policy = enable_permissions_policy
        
        # Default CSP directives
        self.csp_directives = csp_directives or {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", 'data:', 'https:'],
            'font-src': ["'self'", 'data:'],
            'connect-src': ["'self'"],
            'frame-src': ["'self'"],
            'frame-ancestors': ["'self'"],
            'form-action': ["'self'"],
            'object-src': ["'none'"],
            'base-uri': ["'self'"],
            'upgrade-insecure-requests': [],
        }
        
        # Default Feature-Policy directives
        self.feature_policy_directives = feature_policy_directives or {
            'accelerometer': ["'none'"],
            'camera': ["'none'"],
            'geolocation': ["'none'"],
            'gyroscope': ["'none'"],
            'magnetometer': ["'none'"],
            'microphone': ["'none'"],
            'payment': ["'none'"],
            'usb': ["'none'"],
        }
        
        # Default Permissions-Policy directives
        self.permissions_policy_directives = permissions_policy_directives or {
            'accelerometer': '()',
            'camera': '()',
            'geolocation': '()',
            'gyroscope': '()',
            'magnetometer': '()',
            'microphone': '()',
            'payment': '()',
            'usb': '()',
        }
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers to the response."""
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to the response."""
        headers = response.headers
        
        # Content Security Policy
        if self.enable_csp:
            csp_parts = []
            for directive, sources in self.csp_directives.items():
                if sources:
                    csp_parts.append(f"{directive} {' '.join(sources)};")
                else:
                    csp_parts.append(f"{directive};")
            headers['Content-Security-Policy'] = ' '.join(csp_parts)
        
        # HTTP Strict Transport Security
        if self.enable_hsts:
            headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # X-Content-Type-Options
        if self.enable_nosniff:
            headers['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        if self.enable_frame_options:
            headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # X-XSS-Protection
        if self.enable_xss:
            headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        if self.enable_referrer_policy:
            headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature-Policy
        if self.enable_feature_policy and self.feature_policy_directives:
            policy_parts = []
            for feature, sources in self.feature_policy_directives.items():
                policy_parts.append(f"{feature} {' '.join(sources)};")
            headers['Feature-Policy'] = ' '.join(policy_parts)
        
        # Permissions-Policy (replaces Feature-Policy)
        if self.enable_permissions_policy and self.permissions_policy_directives:
            policy_parts = []
            for feature, allowlist in self.permissions_policy_directives.items():
                policy_parts.append(f"{feature}={allowlist}")
            headers['Permissions-Policy'] = ', '.join(policy_parts)
        
        # Certificate Transparency
        if self.enable_expect_ct:
            headers['Expect-CT'] = 'max-age=86400, enforce'

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(
        self,
        app: ASGIApp,
        *,
        logger: Optional[logging.Logger] = None,
        skip_paths: Optional[List[str]] = None,
        skip_path_regex: Optional[str] = None,
        max_body_size: int = 1024,  # Max body size to log in bytes
        sensitive_headers: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.logger = logger or logging.getLogger('http')
        self.skip_paths = set(skip_paths or [])
        self.skip_path_regex = re.compile(skip_path_regex) if skip_path_regex else None
        self.max_body_size = max_body_size
        self.sensitive_headers = set((sensitive_headers or []) + ['authorization', 'cookie', 'set-cookie'])
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip logging for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        if self.skip_path_regex and self.skip_path_regex.match(request.url.path):
            return await call_next(request)
        
        # Log request
        start_time = time.time()
        request_id = request.headers.get('x-request-id', 'unknown')
        
        # Log request details
        self.logger.info(
            f"Request: {request.method} {request.url.path} | "
            f"Request ID: {request_id} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            self.logger.error(
                f"Request failed: {request.method} {request.url.path} | "
                f"Request ID: {request_id} | "
                f"Error: {str(e)}",
                exc_info=True
            )
            raise
        
        # Calculate processing time
        process_time = (time.time() - start_time) * 1000
        
        # Log response
        self.logger.info(
            f"Response: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Process Time: {process_time:.2f}ms | "
            f"Request ID: {request_id}"
        )
        
        return response

def setup_security_middleware(app: ASGIApp) -> None:
    """Set up all security middleware for the FastAPI application."""
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add request logging middleware
    app.add_middleware(
        RequestLoggingMiddleware,
        logger=logging.getLogger('http'),
        skip_paths=['/health', '/metrics'],
        sensitive_headers=['authorization', 'cookie', 'set-cookie']
    )
