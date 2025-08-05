#!/usr/bin/env python3
"""
Credential Manager for OPRYXX_LOGS2

This script provides a command-line interface for managing credentials and secrets.
It integrates with the secure configuration system and supports credential rotation.
"""
import os
import sys
import json
import logging
import argparse
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.security.config_manager import ConfigManager, get_config_manager
from core.security.env_loader import EnvLoader, get_env_loader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages credentials and secrets for the application."""
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.env_loader = get_env_loader()
        self.credential_store = {}
    
    def load_credentials(self, force: bool = False) -> Dict[str, Any]:
        """Load credentials from secure storage."""
        if not self.credential_store or force:
            try:
                # Load from environment variables first
                self.credential_store = {
                    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
                    'GITLAB_TOKEN': os.getenv('GITLAB_TOKEN'),
                    'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
                    'DATABASE_URL': os.getenv('DATABASE_URL'),
                    # Add other credentials as needed
                }
                
                # Load from secure config
                config = self.config_manager.get_config('security')
                if hasattr(config, 'encryption_key'):
                    self.credential_store['ENCRYPTION_KEY'] = config.encryption_key
                
                logger.info("Successfully loaded credentials")
                
            except Exception as e:
                logger.error(f"Failed to load credentials: {e}")
                raise
                
        return self.credential_store
    
    def rotate_credentials(self, key: str = None) -> bool:
        """Rotate credentials.
        
        Args:
            key: Specific credential key to rotate. If None, rotate all credentials.
            
        Returns:
            bool: True if rotation was successful, False otherwise.
        """
        try:
            if key:
                return self._rotate_single_credential(key)
            else:
                # Rotate all credentials
                credentials = self.load_credentials()
                for cred_key in credentials:
                    if not self._rotate_single_credential(cred_key):
                        logger.warning(f"Failed to rotate credential: {cred_key}")
                return True
                
        except Exception as e:
            logger.error(f"Credential rotation failed: {e}")
            return False
    
    def _rotate_single_credential(self, key: str) -> bool:
        """Rotate a single credential."""
        try:
            # Generate a new secure value
            new_value = self._generate_secure_value()
            
            # Update the credential in secure storage
            if key == 'ENCRYPTION_KEY':
                # Special handling for encryption key
                self.config_manager.rotate_secrets()
            else:
                # Update environment variable
                os.environ[key] = new_value
                self.env_loader.set(key, new_value, override=True)
            
            logger.info(f"Successfully rotated credential: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate credential {key}: {e}")
            return False
    
    def _generate_secure_value(self, length: int = 32) -> str:
        """Generate a secure random value."""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def list_credentials(self) -> List[str]:
        """List all available credentials."""
        credentials = self.load_credentials()
        return list(credentials.keys())
    
    def get_credential(self, key: str, mask: bool = True) -> Optional[str]:
        """Get a specific credential value."""
        credentials = self.load_credentials()
        value = credentials.get(key)
        
        if value and mask:
            if len(value) > 8:
                return f"{value[:2]}...{value[-2:]}"
            return "*" * len(value)
            
        return value

def main():
    """Command-line interface for credential management."""
    parser = argparse.ArgumentParser(description='OPRYXX_LOGS2 Credential Manager')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all credentials')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a specific credential')
    get_parser.add_argument('key', help='Credential key to get')
    get_parser.add_argument('--show', action='store_true', 
                          help='Show full credential value (use with caution)')
    
    # Rotate command
    rotate_parser = subparsers.add_parser('rotate', 
                                         help='Rotate credentials')
    rotate_parser.add_argument('--key', help='Specific credential key to rotate')
    rotate_parser.add_argument('--force', action='store_true',
                             help='Force rotation without confirmation')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate',
                                          help='Generate a secure value')
    generate_parser.add_argument('--length', type=int, default=32,
                               help='Length of the generated value')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        manager = CredentialManager()
        
        if args.command == 'list':
            credentials = manager.list_credentials()
            print("\nAvailable credentials:")
            for cred in credentials:
                print(f"- {cred}")
                
        elif args.command == 'get':
            value = manager.get_credential(args.key, mask=not args.show)
            if value is not None:
                print(f"{args.key}: {value}")
            else:
                print(f"Credential not found: {args.key}", file=sys.stderr)
                return 1
                
        elif args.command == 'rotate':
            if args.key:
                print(f"Rotating credential: {args.key}")
            else:
                print("Rotating all credentials")
                
            if not args.force:
                confirm = input("Are you sure you want to proceed? (y/N): ")
                if confirm.lower() != 'y':
                    print("Operation cancelled")
                    return 0
                    
            if manager.rotate_credentials(args.key):
                print("Rotation completed successfully")
            else:
                print("Rotation failed", file=sys.stderr)
                return 1
                
        elif args.command == 'generate':
            print(manager._generate_secure_value(args.length))
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
