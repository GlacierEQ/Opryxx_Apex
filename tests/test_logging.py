"""
Tests for the logging system.
"""
import logging
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.logging import Logger

class TestLogger:
    """Test suite for Logger class."""
    
    def test_singleton_pattern(self):
        """Test that Logger follows singleton pattern."""
        logger1 = Logger()
        logger2 = Logger()
        
        assert logger1 is logger2
    
    def test_logger_initialization(self, tmp_path):
        """Test logger initialization with custom log directory."""
        log_dir = tmp_path / "custom_logs"
        logger = Logger(log_dir=str(log_dir))
        
        assert log_dir.exists()
        assert logger.log_dir == str(log_dir)
        
        # Cleanup
        logger.shutdown()
    
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_logger_handlers(self, mock_stream, mock_file, tmp_path):
        """Test logger handlers setup."""
        log_dir = tmp_path / "test_logs"
        logger = Logger(log_dir=str(log_dir))
        
        # Verify file handler was created
        mock_file.assert_called_once()
        
        # Verify stream handler was created
        mock_stream.assert_called_once()
        
        logger.shutdown()
    
    def test_log_levels(self, caplog):
        """Test logging at different levels."""
        logger = Logger()
        
        test_messages = [
            (logger.debug, "debug message"),
            (logger.info, "info message"),
            (logger.warning, "warning message"),
            (logger.error, "error message"),
            (logger.critical, "critical message")
        ]
        
        for log_func, message in test_messages:
            log_func(message)
            
        # Verify log records were created
        assert len(caplog.records) == len(test_messages)
        
        logger.shutdown()
    
    def test_performance_logging(self, caplog):
        """Test performance logging."""
        logger = Logger()
        
        logger.performance("test_operation", 0.123, {"items": 10})
        
        # Verify performance log was created
        assert any("PERFORMANCE" in r.message for r in caplog.records)
        
        logger.shutdown()
    
    def test_security_logging(self, caplog):
        """Test security event logging."""
        logger = Logger()
        
        logger.security("login_attempt", "WARNING", {"user": "test", "ip": "127.0.0.1"})
        
        # Verify security log was created
        assert any("SECURITY" in r.message for r in caplog.records)
        
        logger.shutdown()
    
    def test_log_rotation(self, tmp_path):
        """Test log file rotation."""
        log_dir = tmp_path / "rotated_logs"
        logger = Logger(log_dir=str(log_dir), max_size_mb=1, backup_count=3)
        
        # Create a large log entry to trigger rotation
        large_message = "x" * 1024 * 1024  # 1MB
        for _ in range(2):  # Trigger rotation
            logger.info(large_message)
        
        # Verify log files were created
        log_files = list(log_dir.glob("*.log*"))
        assert len(log_files) >= 1  # At least one log file should exist
        
        logger.shutdown()
    
    def test_log_formatting(self, caplog):
        """Test log message formatting."""
        logger = Logger()
        
        test_extra = {"key1": "value1", "key2": 42}
        logger.info("Test message", extra=test_extra)
        
        # Verify log record contains extra fields
        record = caplog.records[0]
        assert hasattr(record, 'key1')
        assert hasattr(record, 'key2')
        assert record.key1 == "value1"
        assert record.key2 == 42
        
        logger.shutdown()
    
    def test_shutdown(self):
        """Test logger shutdown."""
        logger = Logger()
        
        # Add a mock handler
        mock_handler = MagicMock()
        logger.logger.addHandler(mock_handler)
        
        # Shutdown the logger
        logger.shutdown()
        
        # Verify handler was removed and closed
        assert mock_handler not in logger.logger.handlers
        mock_handler.close.assert_called_once()
    
    def test_context_manager(self):
        """Test logger as a context manager."""
        with Logger() as logger:
            assert logger is not None
            assert len(logger.logger.handlers) > 0
            
        # Logger should be shut down after context
        assert len(logger.logger.handlers) == 0
