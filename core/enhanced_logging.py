import logging
import logging.handlers
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class EnhancedLogger:
    """Advanced logging system with multiple outputs and analysis"""

    def __init__(self, name: str = "OPRYXX"):
        self.name = name
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Create multiple loggers
        self.setup_loggers()

    def setup_loggers(self):
        """Setup multiple specialized loggers"""

        # Main system logger
        self.system_logger = self._create_logger(
            "system",
            self.log_dir / "system.log",
            logging.INFO
        )

        # Error logger
        self.error_logger = self._create_logger(
            "errors",
            self.log_dir / "errors.log",
            logging.ERROR
        )

        # Performance logger
        self.perf_logger = self._create_logger(
            "performance",
            self.log_dir / "performance.log",
            logging.DEBUG
        )

        # Recovery operations logger
        self.recovery_logger = self._create_logger(
            "recovery",
            self.log_dir / "recovery.log",
            logging.INFO
        )

    def _create_logger(self, name: str, log_file: Path, level: int) -> logging.Logger:
        """Create a configured logger"""
        logger = logging.getLogger(f"{self.name}.{name}")
        logger.setLevel(level)

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )

        # Console handler
        console_handler = logging.StreamHandler()

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def log_recovery_operation(self, operation: str, details: Dict[str, Any], success: bool):
        """Log recovery operation with structured data"""
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'operation': operation,
            'details': details,
            'success': success,
            'duration': details.get('duration', 0)
        }

        self.recovery_logger.info(json.dumps(log_entry))

    def log_system_state(self, state: Dict[str, Any]):
        """Log current system state"""
        self.system_logger.info(
            "System state: %s",
            json.dumps(state, indent=2, default=str)
        )
