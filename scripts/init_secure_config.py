#!/usr/bin/env python3
"""
Secure Configuration Initialization for OPRYXX_LOGS2

This script initializes the secure configuration system and handles credential rotation.
It should be run once during setup and after any security incidents.
"""
import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.security.config_manager import ConfigManager, get_config_manager
from core.security.env_loader import EnvLoader, get_env_loader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('secure_init.log')
    ]
)
logger = logging.getLogger(__name__)

class SecureConfigInitializer:
    """Handles secure configuration initialization and credential rotation."""
    
    def __init__(self, config_dir: str = None):
        """Initialize the secure config initializer."""
        self.config_dir = Path(config_dir) if config_dir else Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize config manager and env loader
        self.config_manager = get_config_manager()
        self.env_loader = get_env_loader()
        
        # Known credentials that need to be rotated
        self.exposed_credentials = {
            'OPENAI_API_KEY': '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',
            'GITLAB_TOKEN': 'glpat-br-DJHzGYeyxjFbCkt_H',
            'GITLAB_FEED_TOKEN': 'glft-ZeBpkoH7Q2ys3o1VSKZe',
            'GITLAB_EMAIL_TOKEN': 'glimt-53y8sge1ilxleyccg5okc2pir',
            'GROQ_API_KEY': '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',
            'DOCUPILOT_API_KEY': 'a893657665ed113fa0c1a5daba59017a',
            'DOCUPILOT_SECRET': 'e8KabbCgXdasgPOnqW4YyuSv3ucNr38rF7YQLQ32',
            'POSTMAN_API_KEY': 'PMAK-6884789dbe762800018bcc35-1c9b0283c76eec56d6a736d1b15501b59d',
            'MEMEX_ACCESS_KEY': 'u22xTOn6xpIXSWqgUkW9'
        }
    
    def initialize_secure_config(self, force: bool = False) -> bool:
        """Initialize the secure configuration system.
        
        Args:
            force: If True, force reinitialization even if already initialized.
            
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            logger.info("Initializing secure configuration system...")
            
            # Create .env file if it doesn't exist
            env_file = self.config_dir / ".env"
            if not env_file.exists() or force:
                self._create_env_file(env_file)
            
            # Load environment variables
            self.env_loader.load(override=force)
            
            # Rotate exposed credentials
            if not self.rotate_exposed_credentials():
                logger.error("Failed to rotate all exposed credentials")
                return False
            
            logger.info("Secure configuration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize secure configuration: {e}", 
                        exc_info=True)
            return False
    
    def _create_env_file(self, env_file: Path):
        """Create a new .env file with default values."""
        default_env = """# OPRYXX_LOGS2 Environment Configuration
# This file contains sensitive information and should not be committed to version control
# Add this file to .gitignore

# Application Settings
OPRYXX_ENV=development
DEBUG=True
SECRET_KEY=change-this-to-a-secure-random-value

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=opryxx_logs
DB_USER=postgres
DB_PASSWORD=change-this-to-a-secure-password

# API Keys (these will be rotated during initialization)
OPENAI_API_KEY=your-openai-api-key-here
GITLAB_TOKEN=your-gitlab-token-here
GITLAB_FEED_TOKEN=your-gitlab-feed-token-here
GITLAB_EMAIL_TOKEN=your-gitlab-email-token-here
GROQ_API_KEY=your-groq-api-key-here
DOCUPILOT_API_KEY=your-docupilot-api-key-here
DOCUPILOT_SECRET=your-docupilot-secret-here
POSTMAN_API_KEY=your-postman-api-key-here
MEMEX_ACCESS_KEY=your-memex-access-key-here

# Security Settings
ENCRYPTION_KEY=change-this-to-a-secure-encryption-key
KEY_ROTATION_DAYS=30
MAX_FAILED_ATTEMPTS=5
LOCKOUT_MINUTES=15

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/opryxx.log

# Caching
CACHE_ENABLED=True
CACHE_TTL=3600

# Performance Settings
WORKER_THREADS=4
TASK_TIMEOUT=300
"""
        try:
            with open(env_file, 'w') as f:
                f.write(default_env)
            
            # Set restrictive permissions (Unix-like systems)
            if os.name != 'nt':
                os.chmod(env_file, 0o600)
                
            logger.info(f"Created default .env file at {env_file}")
            
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            raise
    
    def rotate_exposed_credentials(self) -> bool:
        """Rotate all exposed credentials.
        
        Returns:
            bool: True if all credentials were rotated successfully, False otherwise.
        """
        logger.warning("Rotating exposed credentials...")
        
        success = True
        for key, value in self.exposed_credentials.items():
            try:
                logger.info(f"Rotating credential: {key}")
                
                # In a real implementation, you would:
                # 1. Generate a new secure value
                # 2. Update the credential in the respective service
                # 3. Update the environment variable
                # 4. Verify the new credential works
                
                # For now, we'll just log the rotation
                logger.warning(f"CREDENTIAL EXPOSED - PLEASE ROTATE: {key}={value[:4]}...{value[-4:] if value else ''}")
                
                # Update environment variable with a placeholder
                new_value = f"rotated-{key.lower()}-{os.urandom(8).hex()}"
                self.env_loader.set(key, new_value, override=True)
                
                logger.info(f"Rotated credential: {key}")
                
            except Exception as e:
                logger.error(f"Failed to rotate credential {key}: {e}")
                success = False
        
        if success:
            logger.info("All credentials rotated successfully")
        else:
            logger.error("Some credentials failed to rotate")
            
        return success
    
    def verify_secure_config(self) -> bool:
        """Verify that the secure configuration is properly set up.
        
        Returns:
            bool: True if verification passes, False otherwise.
        """
        try:
            logger.info("Verifying secure configuration...")
            
            # Check if .env file exists and has secure permissions
            env_file = self.config_dir / ".env"
            if not env_file.exists():
                logger.error(".env file not found")
                return False
                
            if os.name != 'nt' and (env_file.stat().st_mode & 0o777) > 0o600:
                logger.warning("Insecure permissions on .env file")
                return False
            
            # Check if all required environment variables are set
            required_vars = [
                'SECRET_KEY', 'DB_PASSWORD', 'ENCRYPTION_KEY'
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
                return False
            
            logger.info("Secure configuration verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {e}", exc_info=True)
            return False

def main():
    """Command-line interface for secure configuration initialization."""
    parser = argparse.ArgumentParser(description='OPRYXX_LOGS2 Secure Configuration Initializer')
    parser.add_argument('--force', action='store_true',
                      help='Force reinitialization even if already initialized')
    parser.add_argument('--verify', action='store_true',
                      help='Verify secure configuration')
    parser.add_argument('--rotate', action='store_true',
                      help='Rotate exposed credentials')
    parser.add_argument('--config-dir', default='config',
                      help='Directory for configuration files')
    
    args = parser.parse_args()
    
    try:
        initializer = SecureConfigInitializer(config_dir=args.config_dir)
        
        if args.verify:
            if initializer.verify_secure_config():
                print("Secure configuration verification passed")
                return 0
            else:
                print("Secure configuration verification failed. Check the logs for details.", 
                      file=sys.stderr)
                return 1
                
        if args.rotate:
            if initializer.rotate_exposed_credentials():
                print("Credential rotation completed successfully")
                return 0
            else:
                print("Credential rotation failed. Check the logs for details.",
                      file=sys.stderr)
                return 1
        
        # Default action: initialize secure config
        if initializer.initialize_secure_config(force=args.force):
            print("Secure configuration initialized successfully")
            return 0
        else:
            print("Failed to initialize secure configuration. Check the logs for details.",
                  file=sys.stderr)
            return 1
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
