"""
OPRYXX Core Module
"""

# Core imports with error handling
try:
    from .config import Config, get_config
except ImportError:
    class Config:
        def __init__(self):
            pass
    def get_config():
        return Config()

try:
    from .performance_monitor import performance_monitor
except ImportError:
    performance_monitor = None

try:
    from .memory_optimizer import memory_optimizer
except ImportError:
    memory_optimizer = None

try:
    from .gpu_acceleration import accelerator
except ImportError:
    accelerator = None

__all__ = ['Config', 'get_config', 'performance_monitor', 'memory_optimizer', 'accelerator']
