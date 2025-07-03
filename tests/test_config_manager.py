"""
Tests for the ConfigManager class
"""

import os
import tempfile
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.config.manager import ConfigManager, ConfigSource, ConfigFormat, config

# Test data
TEST_YAML = """
database:
  host: localhost
  port: 5432
  name: test_db
  enabled: true
  timeout: 3.5
"""

TEST_JSON = """
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true
  }
}
"""

TEST_TOML = """
[app]
name = "test_app"
version = "1.0.0"

[features]
analytics = true
notifications = false
"""

class TestConfigManager:
    def setup_method(self):
        """Reset the config manager before each test"""
        # Clear the singleton instance
        ConfigManager._instance = None
        ConfigManager._initialized = False
        
        # Create a new instance
        self.manager = ConfigManager()
    
    def test_singleton_pattern(self):
        """Test that ConfigManager is a singleton"""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        assert manager1 is manager2
        assert manager1 is config
    
    def test_add_yaml_source(self, tmp_path):
        """Test adding a YAML config source"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(TEST_YAML)
        
        source = ConfigSource(
            path=str(config_file),
            format=ConfigFormat.YAML,
            required=True
        )
        
        assert self.manager.add_source(source) is True
        assert self.manager["database.host"] == "localhost"
        assert self.manager["database.port"] == 5432
        assert self.manager["database.enabled"] is True
        assert self.manager["database.timeout"] == 3.5
    
    def test_add_json_source(self, tmp_path):
        """Test adding a JSON config source"""
        config_file = tmp_path / "test_config.json"
        config_file.write_text(TEST_JSON)
        
        assert self.manager.add_source(
            str(config_file),
            format=ConfigFormat.JSON
        ) is True
        
        assert self.manager["server.host"] == "0.0.0.0"
        assert self.manager["server.port"] == 8000
        assert self.manager["server.debug"] is True
    
    def test_add_toml_source(self, tmp_path):
        """Test adding a TOML config source"""
        config_file = tmp_path / "test_config.toml"
        config_file.write_text(TEST_TOML)
        
        assert self.manager.add_source(
            str(config_file),
            format=ConfigFormat.TOML
        ) is True
        
        assert self.manager["app.name"] == "test_app"
        assert self.manager["app.version"] == "1.0.0"
        assert self.manager["features.analytics"] is True
        assert self.manager["features.notifications"] is False
    
    def test_env_overrides(self, tmp_path, monkeypatch):
        """Test environment variable overrides"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(TEST_YAML)
        
        # Set environment variables with prefix
        monkeypatch.setenv("APP_DATABASE__HOST", "db.example.com")
        monkeypatch.setenv("APP_DATABASE__PORT", "6432")
        monkeypatch.setenv("APP_DATABASE__ENABLED", "false")
        
        self.manager.add_source(
            str(config_file),
            format=ConfigFormat.YAML,
            env_prefix="APP_"
        )
        
        assert self.manager["database.host"] == "db.example.com"
        assert self.manager["database.port"] == 6432  # Should be int
        assert self.manager["database.enabled"] is False  # Should be bool
    
    def test_missing_optional_source(self, tmp_path):
        """Test handling of missing optional config source"""
        missing_file = tmp_path / "missing_config.yaml"
        
        assert self.manager.add_source(
            str(missing_file),
            format=ConfigFormat.YAML,
            required=False
        ) is False
    
    def test_missing_required_source(self, tmp_path):
        """Test handling of missing required config source"""
        missing_file = tmp_path / "missing_required.yaml"
        
        with pytest.raises(FileNotFoundError):
            self.manager.add_source(
                str(missing_file),
                format=ConfigFormat.YAML,
                required=True
            )
    
    def test_nonexistent_key(self):
        """Test handling of non-existent keys"""
        with pytest.raises(KeyError):
            _ = self.manager["nonexistent.key"]
        
        # Test default value
        assert self.manager.get("nonexistent.key", "default") == "default"
    
    def test_to_dict(self, tmp_path):
        """Test exporting config to dictionary"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(TEST_YAML)
        
        self.manager.add_source(str(config_file), format=ConfigFormat.YAML)
        
        config_dict = self.manager.to_dict()
        assert config_dict["database"]["host"] == "localhost"
        assert config_dict["database"]["port"] == 5432
    
    def test_get_section(self, tmp_path):
        """Test getting a configuration section"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(TEST_YAML)
        
        self.manager.add_source(str(config_file), format=ConfigFormat.YAML)
        
        db_section = self.manager.get_section("database")
        assert db_section["host"] == "localhost"
        assert db_section["port"] == 5432
    
    @pytest.mark.skip(reason="File system watching is tricky to test")
    def test_file_watching(self, tmp_path):
        """Test file watching functionality"""
        import time
        
        # Create a test config file
        config_file = tmp_path / "watch_test.yaml"
        config_file.write_text(TEST_YAML)
        
        # Set up a mock callback
        callback_called = False
        
        def mock_callback(event):
            nonlocal callback_called
            callback_called = True
        
        # Add the config source with watching enabled
        self.manager.subscribe(mock_callback)
        self.manager.add_source(
            str(config_file),
            format=ConfigFormat.YAML,
            watch=True
        )
        
        # Modify the file
        with open(config_file, 'w') as f:
            f.write("database:\n  host: updated")
        
        # Wait for the watcher to trigger
        time.sleep(1)
        
        # Process events
        self.manager.reload()
        
        # Check if the callback was called
        assert callback_called is True
        assert self.manager["database.host"] == "updated"
    
    def test_validation(self, tmp_path):
        """Test configuration validation with Pydantic"""
        from pydantic import BaseModel, PositiveInt
        
        # Define a schema
        class DatabaseConfig(BaseModel):
            host: str
            port: PositiveInt
            name: str
            enabled: bool = True
        
        class AppConfig(BaseModel):
            database: DatabaseConfig
        
        # Create a valid config
        config_file = tmp_path / "valid_config.yaml"
        config_file.write_text("""
        database:
          host: localhost
          port: 5432
          name: test_db
          enabled: true
        """)
        
        self.manager.add_source(str(config_file), format=ConfigFormat.YAML)
        assert self.manager.validate(AppConfig) is True
        
        # Create an invalid config
        invalid_file = tmp_path / "invalid_config.yaml"
        invalid_file.write_text("""
        database:
          host: localhost
          port: -1  # Invalid port
          name: test_db
        """)
        
        self.manager.add_source(str(invalid_file), format=ConfigFormat.YAML, required=False)
        assert self.manager.validate(AppConfig) is False

# Test the global config instance
def test_global_config(tmp_path):
    """Test the global config instance"""
    config_file = tmp_path / "global_test.yaml"
    config_file.write_text(TEST_YAML)
    
    # Reset the global instance
    ConfigManager._instance = None
    ConfigManager._initialized = False
    
    # Get the global instance and add a source
    cfg = config
    cfg.add_source(str(config_file), format=ConfigFormat.YAML)
    
    assert cfg["database.host"] == "localhost"
