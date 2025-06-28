"""
Tests for the configuration management system.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from core.config import ConfigManager

class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    def test_initialization(self, tmp_path):
        """Test ConfigManager initialization."""
        config_dir = tmp_path / "config"
        manager = ConfigManager(config_dir=str(config_dir))
        
        assert manager.config_dir == str(config_dir)
        assert isinstance(manager._config, dict)
        assert config_dir.exists()
    
    def test_load_config_file_not_found(self, config_manager):
        """Test loading non-existent config file."""
        with pytest.raises(FileNotFoundError):
            config_manager.load_config("nonexistent.yaml")
    
    @patch("yaml.safe_load")
    @patch("builtins.open", new_callable=mock_open, read_data="test: value")
    def test_load_config_success(self, mock_file, mock_yaml, config_manager):
        """Test successful config file loading."""
        mock_yaml.return_value = {"test": "value"}
        
        config = config_manager.load_config("test_config.yaml")
        
        assert config == {"test": "value"}
        mock_file.assert_called_once()
    
    def test_get_config_value(self, config_manager):
        """Test getting configuration values."""
        config_manager._config = {"section": {"key": "value"}}
        
        value = config_manager.get("section", "key")
        
        assert value == "value"
    
    def test_get_nonexistent_value(self, config_manager):
        """Test getting non-existent configuration value."""
        with pytest.raises(KeyError):
            config_manager.get("nonexistent", "key")
    
    def test_get_with_default(self, config_manager):
        """Test getting configuration value with default."""
        value = config_manager.get("nonexistent", "key", default="default")
        assert value == "default"
    
    def test_set_config_value(self, config_manager):
        """Test setting configuration values."""
        config_manager.set("section", "key", "new_value")
        
        assert config_manager._config["section"]["key"] == "new_value"
    
    @patch("yaml.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_config(self, mock_file, mock_yaml, config_manager, tmp_path):
        """Test saving configuration to file."""
        test_file = tmp_path / "test_config.yaml"
        config_manager._config = {"test": "value"}
        
        config_manager.save_config(str(test_file))
        
        mock_file.assert_called_once_with(test_file, 'w', encoding='utf-8')
        mock_yaml.assert_called_once()
    
    def test_register_validator(self, config_manager):
        """Test registering a configuration validator."""
        def validator(section, key, value):
            return True
            
        config_manager.register_validator("section", "key", validator)
        
        assert len(config_manager._validators[("section", "key")]) == 1
    
    def test_validation_failure(self, config_manager):
        """Test configuration validation failure."""
        def validator(section, key, value):
            return False, "Invalid value"
            
        config_manager.register_validator("section", "key", validator)
        
        with pytest.raises(ValueError) as excinfo:
            config_manager.set("section", "key", "invalid")
            
        assert "Invalid value" in str(excinfo.value)
