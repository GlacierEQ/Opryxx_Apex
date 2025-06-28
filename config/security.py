"""
Security configuration and utilities for OPRYXX.
"""
import os
import secrets
from typing import Dict, List, Optional, Union
from datetime import timedelta
from pathlib import Path

from pydantic import BaseSettings, Field, validator
from pydantic.networks import AnyHttpUrl


class SecurityConfig(BaseSettings):
    """Security configuration settings."""
    
    # Security headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline';",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    }
    
    # CORS settings
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost",
        "http://localhost:8000",
    ]
    
    # Rate limiting
    RATE_LIMIT: str = "1000/day;100/hour;10/minute"
    
    # Session security
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # CSRF protection
    CSRF_COOKIE_SECURE: bool = True
    CSRF_COOKIE_HTTPONLY: bool = True
    
    # JWT settings
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(64),
        description="Secret key for JWT token signing"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Password hashing
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    PASSWORD_HASH_ITERATIONS: int = 10000
    
    # API security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY_LENGTH: int = 32
    
    # Security logging
    LOG_SENSITIVE_DATA: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return SecurityConfig()


def generate_secure_random(length: int = 32) -> str:
    """Generate a secure random string."""
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    import bcrypt
    
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    import bcrypt
    
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_strength(password: str) -> str:
    """Check password strength."""
    import zxcvbn
    
    result = zxcvbn.zxcvbn(password)
    score = result["score"]
    
    if score >= 4:
        return "very_strong"
    elif score == 3:
        return "strong"
    elif score == 2:
        return "moderate"
    elif score == 1:
        return "weak"
    return "very_weak"


def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    import html
    import re
    
    # Remove any HTML/JS tags
    clean = re.sub(r'<[^>]*>', '', input_str)
    # Escape HTML entities
    clean = html.escape(clean)
    return clean.strip()


# Initialize security configuration
security_config = get_security_config()
