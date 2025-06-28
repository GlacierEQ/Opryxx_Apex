"""
Test configuration and fixtures for OPRYXX tests.
"""
import os
import sys
import pytest
from pathlib import Path
from typing import Generator, Any, Dict

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core components for testing
from core.config import ConfigManager
from core.logging import Logger

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Return test configuration."""
    return {
        "test": {
            "test_key": "test_value"
        },
        "database": {
            "test_db": "sqlite:///:memory:"
        }
    }

@pytest.fixture(scope="function")
def config_manager(test_config: Dict[str, Any]) -> ConfigManager:
    """Create a ConfigManager instance for testing."""
    manager = ConfigManager()
    # Override with test config
    manager._config = test_config
    return manager

@pytest.fixture(scope="function")
def logger() -> Generator[Logger, None, None]:
    """Create a Logger instance for testing."""
    logger = Logger()
    yield logger
    # Cleanup after test
    logger.shutdown()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Create test directories if they don't exist
    test_dirs = [
        "tests/data",
        "tests/logs",
        "tests/temp"
    ]
    
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    yield  # This is where the testing happens
    
    # Cleanup after all tests complete
    # Remove test directories if they exist and are empty
    for dir_path in test_dirs:
        try:
            os.removedirs(dir_path)
        except OSError:
            pass  # Directory not empty or doesn't exist
