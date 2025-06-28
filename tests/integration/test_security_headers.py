"""Integration tests for security headers in FastAPI responses."""
import pytest
from fastapi.testclient import TestClient
from ai_workbench.api.app import create_app
from ai_workbench.api.middleware.security import SecurityHeadersMiddleware

# List of security headers we expect to be set
REQUIRED_SECURITY_HEADERS = [
    'Content-Security-Policy',
    'Strict-Transport-Security',
    'X-Content-Type-Options',
    'X-Frame-Options',
    'X-XSS-Protection',
    'Referrer-Policy',
    'Permissions-Policy',
]

# Headers that should never be exposed
FORBIDDEN_HEADERS = [
    'Server',
    'X-Powered-By',
    'X-AspNet-Version',
    'X-AspNetMvc-Version',
]

@pytest.fixture
def test_client():
    """Create a test client with the FastAPI app."""
    app = create_app(test_config={"TESTING": True})
    return TestClient(app)

def test_security_headers_present(test_client):
    """Test that all required security headers are present in responses."""
    # Make a request to any endpoint
    response = test_client.get("/")
    
    # Check that all required security headers are present
    for header in REQUIRED_SECURITY_HEADERS:
        assert header in response.headers, f"Missing security header: {header}"
    
    # Check that forbidden headers are not present
    for header in FORBIDDEN_HEADERS:
        assert header not in response.headers, f"Forbidden header present: {header}"

def test_csp_header_structure(test_client):
    """Test that the Content-Security-Policy header has the expected structure."""
    response = test_client.get("/")
    csp = response.headers.get('Content-Security-Policy', '')
    
    # Check that the CSP header is not empty
    assert csp, "Content-Security-Policy header is empty"
    
    # Check that it contains some expected directives
    assert "default-src 'self'" in csp
    assert "script-src 'self'" in csp
    assert "object-src 'none'" in csp

def test_hsts_header_values(test_client):
    """Test that the HSTS header has secure values."""
    response = test_client.get("/")
    hsts = response.headers.get('Strict-Transport-Security', '')
    
    assert hsts, "Strict-Transport-Security header is missing"
    assert 'max-age=' in hsts
    assert 'includeSubDomains' in hsts
    assert 'preload' in hsts
    
    # Check that max-age is at least 1 year (31536000 seconds)
    max_age = int(hsts.split('max-age=')[1].split(';')[0])
    assert max_age >= 31536000, "HSTS max-age should be at least 1 year"

def test_xss_protection_header(test_client):
    """Test that XSS protection is enabled."""
    response = test_client.get("/")
    xss_protection = response.headers.get('X-XSS-Protection', '')
    
    assert xss_protection == '1; mode=block', "XSS protection not properly configured"

def test_content_type_options(test_client):
    """Test that MIME type sniffing is disabled."""
    response = test_client.get("/")
    cto = response.headers.get('X-Content-Type-Options', '')
    
    assert cto.lower() == 'nosniff', "MIME type sniffing not disabled"

def test_frame_options(test_client):
    """Test that clickjacking protection is enabled."""
    response = test_client.get("/")
    frame_options = response.headers.get('X-Frame-Options', '')
    
    assert frame_options.upper() == 'SAMEORIGIN', "Frame options not properly configured"

def test_referrer_policy(test_client):
    """Test that referrer policy is set to a secure default."""
    response = test_client.get("/")
    referrer_policy = response.headers.get('Referrer-Policy', '')
    
    # Check for a secure referrer policy
    secure_policies = [
        'strict-origin-when-cross-origin',
        'no-referrer-when-downgrade',
        'strict-origin',
        'no-referrer',
    ]
    
    assert referrer_policy in secure_policies, "Insecure referrer policy"

def test_permissions_policy(test_client):
    """Test that permissions policy is properly configured."""
    response = test_client.get("/")
    permissions_policy = response.headers.get('Permissions-Policy', '')
    
    # Check that certain features are disabled by default
    disabled_features = [
        'camera=()',
        'microphone=()',
        'geolocation=()',
        'payment=()',
    ]
    
    for feature in disabled_features:
        assert feature in permissions_policy, f"Feature {feature} not properly restricted"

def test_cors_headers(test_client):
    """Test that CORS headers are properly configured."""
    # Test preflight request
    response = test_client.options(
        "/",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With",
        },
    )
    
    # Check CORS headers
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
    assert "access-control-allow-credentials" in response.headers.lower()

def test_security_headers_on_error_responses(test_client):
    """Test that security headers are present even on error responses."""
    # Test with a 404 response
    response = test_client.get("/nonexistent-endpoint")
    
    # Should still have security headers
    for header in REQUIRED_SECURITY_HEADERS:
        assert header in response.headers, f"Missing security header on 404: {header}"
    
    # Test with a 500 response
    @test_client.app.get("/test-500")
    def raise_error():
        raise ValueError("Test error")
    
    response = test_client.get("/test-500")
    assert response.status_code == 500
    
    # Should still have security headers
    for header in REQUIRED_SECURITY_HEADERS:
        assert header in response.headers, f"Missing security header on 500: {header}"
