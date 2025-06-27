"""
Authentication and authorization module for OPRYXX.
Handles user authentication, authorization, and security operations.
"""
import os
import uuid
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import logging
import json
import secrets
import string
from pathlib import Path

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

# Configure logging
logger = logging.getLogger(__name__)

# Constants
TOKEN_EXPIRATION = 3600  # 1 hour in seconds
REFRESH_TOKEN_EXPIRATION = 86400 * 7  # 7 days in seconds
PASSWORD_HASH_ITERATIONS = 100000
SALT_LENGTH = 16
TOKEN_ALGORITHM = "HS256"
RSA_KEY_SIZE = 2048

class AuthManager:
    """Handles authentication and authorization operations."""
    
    def __init__(self, config_path: str = "c:/CATHEDRAL/OPRYXX_LOGS/config"):
        """Initialize AuthManager with configuration."""
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize keys
        self._load_or_generate_keys()
        
        # In-memory storage for active sessions (in production, use Redis or similar)
        self.active_sessions: Dict[str, dict] = {}
        self._load_users()
    
    def _load_or_generate_keys(self) -> None:
        """Load or generate encryption and JWT keys."""
        # JWT Secret Key
        self.jwt_secret_path = self.config_path / "jwt_secret.key"
        if self.jwt_secret_path.exists():
            with open(self.jwt_secret_path, "rb") as f:
                self.jwt_secret = f.read()
        else:
            self.jwt_secret = secrets.token_bytes(32)
            with open(self.jwt_secret_path, "wb") as f:
                f.write(self.jwt_secret)
        
        # RSA Key Pair
        self.private_key_path = self.config_path / "private_key.pem"
        self.public_key_path = self.config_path / "public_key.pem"
        
        if self.private_key_path.exists() and self.public_key_path.exists():
            with open(self.private_key_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            with open(self.public_key_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        else:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=RSA_KEY_SIZE,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()
            
            # Save private key
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            with open(self.private_key_path, "wb") as f:
                f.write(private_pem)
            
            # Save public key
            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            with open(self.public_key_path, "wb") as f:
                f.write(public_pem)
    
    def _load_users(self) -> None:
        """Load users from storage."""
        self.users_file = self.config_path / "users.json"
        if self.users_file.exists():
            try:
                with open(self.users_file, "r") as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading users: {e}")
                self.users = {}
        else:
            self.users = {}
            # Create default admin user if no users exist
            if not self.users:
                self._create_default_admin()
    
    def _save_users(self) -> None:
        """Save users to storage."""
        try:
            with open(self.users_file, "w") as f:
                json.dump(self.users, f, indent=4)
        except IOError as e:
            logger.error(f"Error saving users: {e}")
    
    def _create_default_admin(self) -> None:
        """Create a default admin user if none exists."""
        default_password = self._generate_secure_password()
        salt = self._generate_salt()
        hashed_password = self._hash_password(default_password, salt)
        
        self.users["admin"] = {
            "username": "admin",
            "password_hash": hashed_password,
            "salt": salt,
            "roles": ["admin"],
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "password_changed": False
        }
        self._save_users()
        
        logger.warning(f"Default admin user created with password: {default_password}")
        logger.warning("PLEASE CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")
    
    def _generate_salt(self) -> str:
        """Generate a random salt."""
        return secrets.token_hex(SALT_LENGTH)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with a salt."""
        dk = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            PASSWORD_HASH_ITERATIONS
        )
        return base64.b64encode(dk).decode('utf-8')
    
    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Ensure password has at least one of each character type
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and any(c.isdigit() for c in password)
                    and any(c in "!@#$%^&*" for c in password)):
                return password
    
    def create_user(self, username: str, password: str, roles: List[str] = None) -> bool:
        """Create a new user."""
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return False
        
        salt = self._generate_salt()
        hashed_password = self._hash_password(password, salt)
        
        self.users[username] = {
            "username": username,
            "password_hash": hashed_password,
            "salt": salt,
            "roles": roles or ["user"],
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "password_changed": True
        }
        
        self._save_users()
        logger.info(f"User {username} created successfully")
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user and return user data if successful."""
        user = self.users.get(username)
        if not user:
            # Simulate password verification to prevent timing attacks
            self._hash_password(password, self._generate_salt())
            return None
        
        # Verify password
        hashed_password = self._hash_password(password, user["salt"])
        if not hmac.compare_digest(hashed_password, user["password_hash"]):
            return None
        
        # Update last login time
        user["last_login"] = datetime.utcnow().isoformat()
        self._save_users()
        
        return user
    
    def generate_tokens(self, username: str, user_agent: str = "") -> Dict[str, str]:
        """Generate access and refresh tokens for a user."""
        if username not in self.users:
            raise ValueError("User not found")
        
        user = self.users[username]
        now = datetime.utcnow()
        
        # Generate access token
        access_token_payload = {
            "sub": username,
            "roles": user["roles"],
            "iat": now,
            "exp": now + timedelta(seconds=TOKEN_EXPIRATION),
            "type": "access",
            "jti": str(uuid.uuid4())
        }
        
        # Generate refresh token
        refresh_token = secrets.token_urlsafe(64)
        refresh_token_expiry = now + timedelta(seconds=REFRESH_TOKEN_EXPIRATION)
        
        # Store refresh token
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "username": username,
            "refresh_token": refresh_token,
            "user_agent": user_agent,
            "created_at": now.isoformat(),
            "expires_at": refresh_token_expiry.isoformat(),
            "last_used": now.isoformat()
        }
        
        # Sign and return tokens
        access_token = jwt.encode(
            access_token_payload,
            self.jwt_secret,
            algorithm=TOKEN_ALGORITHM
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": TOKEN_EXPIRATION,
            "session_id": session_id
        }
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a JWT token and return its payload if valid."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[TOKEN_ALGORITHM],
                options={"verify_exp": True}
            )
            return payload
        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def refresh_token(self, refresh_token: str, session_id: str) -> Optional[Dict[str, str]]:
        """Refresh an access token using a refresh token."""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        if not hmac.compare_digest(session["refresh_token"], refresh_token):
            return None
        
        now = datetime.utcnow()
        if datetime.fromisoformat(session["expires_at"]) < now:
            del self.active_sessions[session_id]
            return None
        
        # Update session
        session["last_used"] = now.isoformat()
        
        # Generate new access token
        username = session["username"]
        user = self.users.get(username)
        if not user:
            return None
        
        access_token_payload = {
            "sub": username,
            "roles": user["roles"],
            "iat": now,
            "exp": now + timedelta(seconds=TOKEN_EXPIRATION),
            "type": "access",
            "jti": str(uuid.uuid4())
        }
        
        access_token = jwt.encode(
            access_token_payload,
            self.jwt_secret,
            algorithm=TOKEN_ALGORITHM
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": TOKEN_EXPIRATION
        }
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a user session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def revoke_all_sessions(self, username: str) -> int:
        """Revoke all sessions for a user."""
        count = 0
        session_ids = [
            sid for sid, session in self.active_sessions.items()
            if session["username"] == username
        ]
        
        for sid in session_ids:
            del self.active_sessions[sid]
            count += 1
        
        return count
    
    def has_permission(self, user_roles: List[str], required_role: str) -> bool:
        """Check if user has the required role."""
        if "admin" in user_roles:
            return True
        return required_role in user_roles
    
    def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """Change a user's password."""
        user = self.users.get(username)
        if not user:
            return False
        
        # Verify current password
        hashed_password = self._hash_password(current_password, user["salt"])
        if not hmac.compare_digest(hashed_password, user["password_hash"]):
            return False
        
        # Update password
        new_salt = self._generate_salt()
        new_hashed_password = self._hash_password(new_password, new_salt)
        
        user["password_hash"] = new_hashed_password
        user["salt"] = new_salt
        user["password_changed"] = True
        user["last_password_change"] = datetime.utcnow().isoformat()
        
        self._save_users()
        
        # Revoke all active sessions
        self.revoke_all_sessions(username)
        
        return True

# Singleton instance
auth_manager = AuthManager()
