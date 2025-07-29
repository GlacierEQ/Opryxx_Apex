import psutil
import platform
from datetime import datetime

class SystemHealthMonitor:
    def __init__(self):
        self.os = platform.system()
        self.snapshot_time = datetime.now()

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'percent': mem.percent
        }

    def get_disk_usage(self):
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

    def system_health_check(self):
        return {
            'timestamp': self.snapshot_time.isoformat(),
            'os': self.os,
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage()
        }

def system_health_check():
    monitor = SystemHealthMonitor()
    return monitor.system_health_check()
