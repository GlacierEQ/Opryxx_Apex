"""
Security Configuration for OPRYXX System
"""

import os
import hashlib
import secrets

class SecurityConfig:
    def __init__(self):
        self.secure_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
        }
        
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            hash_part, salt = hashed.split(':')
            return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == hash_part
        except:
            return False
    
    def generate_secure_token(self) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(32)
    
    def validate_input(self, input_data: str) -> bool:
        """Basic input validation"""
        dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(', '__import__']
        return not any(pattern in input_data.lower() for pattern in dangerous_patterns)