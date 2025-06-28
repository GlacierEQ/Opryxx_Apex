import psutil
import json
import time
import threading
import logging
import functools
from datetime import datetime
import sqlite3
import numpy as np
from collections import deque
from typing import Dict, Any, List, Optional, Deque, Tuple
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager
from pythonjsonlogger import jsonlogger
from functools import lru_cache

# Set up structured logging
logger = logging.getLogger('system_monitor')
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Custom exception classes
class SystemMonitorError(Exception):
    """Base exception for system monitor errors."""
    pass

class MetricCollectionError(SystemMonitorError):
    """Raised when there's an error collecting metrics."""
    pass

class DatabaseError(SystemMonitorError):
    """Raised for database-related errors."""
    pass

# Utility functions
def handle_errors(default=None):
    """Decorator to handle common exceptions and log them."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except psutil.NoSuchProcess as e:
                logger.warning(f"Process no longer exists: {e}", exc_info=True)
            except psutil.AccessDenied as e:
                logger.error(f"Permission denied: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                if default is not None:
                    return default
                raise
        return wrapper
    return decorator

@dataclass
class SystemMetrics:
    """Data class for system metrics with type hints and default values."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    cpu: Dict[str, Any] = field(default_factory=dict)
    memory: Dict[str, Any] = field(default_factory=dict)
    disk: Dict[str, Any] = field(default_factory=dict)
    network: Dict[str, Any] = field(default_factory=dict)
    processes: Dict[str, Any] = field(default_factory=dict)

class AdvancedSystemMonitor:
    """Advanced system monitoring with caching, error handling, and structured logging."""
    
    def __init__(self, db_path: str = 'ai-workbench/knowledge/system_metrics.db'):
        """Initialize the system monitor with configuration.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.metrics_history = {
            'cpu': deque(maxlen=1000),
            'memory': deque(maxlen=1000),
            'disk': deque(maxlen=1000),
            'network': deque(maxlen=1000),
            'processes': deque(maxlen=100)
        }
        
        self.anomaly_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0
        }
        
        self.learning_enabled = True
        self.prediction_model = None
        self.db_path = db_path
        self._db_lock = threading.RLock()
        self._last_collection_time = 0
        self._collection_interval = 60  # seconds
        
        # Initialize database and logging
        try:
            self.setup_database()
            logger.info("System monitor initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize system monitor: {e}", exc_info=True)
            raise SystemMonitorError("Failed to initialize system monitor") from e

    @contextmanager
    def _get_db_connection(self):
        """Context manager for database connections with error handling."""
        conn = None
        try:
            with self._db_lock:
                conn = sqlite3.connect(self.db_path, timeout=30.0)
                conn.row_factory = sqlite3.Row
                conn.execute('PRAGMA journal_mode=WAL')  # Better concurrency
                yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}", exc_info=True)
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            if conn:
                try:
                    conn.close()
                except sqlite3.Error as e:
                    logger.error(f"Error closing database connection: {e}")

    def setup_database(self):
        """Initialize SQLite database for metrics storage with error handling."""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Enable WAL mode for better concurrency
                cursor.execute('PRAGMA journal_mode=WAL')
                
                # Create metrics table with indexes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        metric_type TEXT NOT NULL,
                        value REAL NOT NULL,
                        metadata TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                    ON metrics(timestamp)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_metrics_type 
                    ON metrics(metric_type)
                ''')

                # Create anomalies table with indexes
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS anomalies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        anomaly_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        details TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved_at DATETIME
                    )
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp 
                    ON anomalies(timestamp)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_anomalies_resolved 
                    ON anomalies(resolved)
                ''')
                
                conn.commit()
                logger.info("Database tables and indexes created/validated")
                
        except Exception as e:
            logger.critical(f"Failed to set up database: {e}", exc_info=True)
            raise DatabaseError("Database setup failed") from e

    @lru_cache(maxsize=128, typed=False)
    @handle_errors(default={})
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics with caching and error handling."""
        try:
            cpu_times = psutil.cpu_times_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_stats = psutil.cpu_stats()
            
            return {
                'usage_percent': psutil.cpu_percent(interval=0.1),
                'per_cpu': psutil.cpu_percent(interval=0.1, percpu=True),
                'times': cpu_times._asdict(),
                'freq': cpu_freq._asdict() if cpu_freq else {},
                'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0],
                'stats': {
                    'ctx_switches': getattr(cpu_stats, 'ctx_switches', 0),
                    'interrupts': getattr(cpu_stats, 'interrupts', 0),
                    'soft_interrupts': getattr(cpu_stats, 'soft_interrupts', 0),
                    'syscalls': getattr(cpu_stats, 'syscalls', 0)
                },
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True)
            }
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}", exc_info=True)
            raise

    @lru_cache(maxsize=64, typed=False)
    @handle_errors(default={})
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics with caching and error handling."""
        try:
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            return {
                'virtual': {
                    'total': virtual_mem.total,
                    'available': virtual_mem.available,
                    'percent': virtual_mem.percent,
                    'used': virtual_mem.used,
                    'free': virtual_mem.free,
                    'active': getattr(virtual_mem, 'active', None),
                    'inactive': getattr(virtual_mem, 'inactive', None),
                    'buffers': getattr(virtual_mem, 'buffers', None),
                    'cached': getattr(virtual_mem, 'cached', None),
                    'shared': getattr(virtual_mem, 'shared', None),
                    'slab': getattr(virtual_mem, 'slab', None)
                },
                'swap': {
                    'total': swap_mem.total,
                    'used': swap_mem.used,
                    'free': swap_mem.free,
                    'percent': swap_mem.percent,
                    'sin': getattr(swap_mem, 'sin', None),
                    'sout': getattr(swap_mem, 'sout', None)
                },
                'usage_trend': self.calculate_trend('memory')
            }
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}", exc_info=True)
            raise

    @handle_errors(default={})
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk metrics with error handling."""
        disk_metrics = {}
        try:
            for partition in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    io_counters = psutil.disk_io_counters(perdisk=False)
                    
                    disk_metrics[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'usage': {
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': usage.percent
                        },
                        'io': io_counters._asdict() if io_counters else {}
                    }
                except (PermissionError, psutil.AccessDenied) as e:
                    logger.warning(f"Permission denied accessing {partition.mountpoint}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error reading disk metrics for {partition.device}: {e}", exc_info=True)
                    continue
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}", exc_info=True)
            raise
        
        return disk_metrics

    @handle_errors(default={})
    def _get_network_metrics(self) -> Dict[str, Any]:
        """Get network metrics with error handling."""
        try:
            io_counters = psutil.net_io_counters()
            connections = psutil.net_connections(kind='inet')
            
            return {
                'io': io_counters._asdict() if io_counters else {},
                'connections': {
                    'total': len(connections),
                    'tcp': len([c for c in connections if c.type == 1]),
                    'udp': len([c for c in connections if c.type == 2]),
                    'listening': len([c for c in connections if c.status == 'LISTEN']),
                    'established': len([c for c in connections if c.status == 'ESTABLISHED']),
                    'time_wait': len([c for c in connections if c.status == 'TIME_WAIT'])
                },
                'interfaces': {
                    name: stats._asdict() 
                    for name, stats in psutil.net_io_counters(pernic=True).items()
                },
                'addresses': {
                    name: [addr._asdict() for addr in addrs] 
                    for name, addrs in psutil.net_if_addrs().items()
                }
            }
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}", exc_info=True)
            raise

    @handle_errors(default=[])
    def _get_process_metrics(self) -> List[Dict[str, Any]]:
        """Get process metrics with error handling and caching."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    with proc.oneshot():  # Minimize system calls
                        processes.append({
                            'pid': proc.pid,
                            'name': proc.name(),
                            'username': proc.username(),
                            'cpu_percent': proc.cpu_percent(),
                            'memory_percent': proc.memory_percent(),
                            'status': proc.status(),
                            'create_time': proc.create_time(),
                            'cmdline': proc.cmdline()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    logger.warning(f"Error getting process info: {e}")
                    continue
            return processes
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}", exc_info=True)
            raise

    def collect_comprehensive_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive system metrics with error handling and caching.
        
        Returns:
            Dict containing all collected metrics
        """
        try:
            # Clear cache if it's time for a fresh collection
            current_time = time.time()
            if current_time - getattr(self, '_last_collection_time', 0) > self._collection_interval:
                self._get_cpu_metrics.cache_clear()
                self._get_memory_metrics.cache_clear()
                self._last_collection_time = current_time
            
            # Collect all metrics in parallel
            with ThreadPoolExecutor() as executor:
                cpu_future = executor.submit(self._get_cpu_metrics)
                mem_future = executor.submit(self._get_memory_metrics)
                disk_future = executor.submit(self._get_disk_metrics)
                net_future = executor.submit(self._get_network_metrics)
                proc_future = executor.submit(self._get_process_metrics)
                
                # Get results with timeout
                cpu_metrics = cpu_future.result(timeout=5)
                memory_metrics = mem_future.result(timeout=5)
                disk_metrics = disk_future.result(timeout=10)
                network_metrics = net_future.result(timeout=5)
                processes = proc_future.result(timeout=15)
            
            # Process top consumers
            top_cpu = sorted(processes, key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)[:10]
            top_memory = sorted(processes, key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)[:10]
            
            # Create metrics object
            metrics = SystemMetrics(
                cpu=cpu_metrics,
                memory=memory_metrics,
                disk=disk_metrics,
                network=network_metrics,
                processes={
                    'total': len(processes),
                    'top_cpu': top_cpu,
                    'top_memory': top_memory
                }
            )
            
            # Store metrics
            metrics_dict = asdict(metrics)
            self.update_metrics_history(metrics_dict)
            self.store_metrics_db(metrics_dict)
            self.detect_anomalies(metrics_dict)
            
            return metrics_dict
            
        except TimeoutError as e:
            logger.error("Timeout while collecting metrics", exc_info=True)
            raise MetricCollectionError("Timeout while collecting metrics") from e
        except Exception as e:
            logger.error("Failed to collect comprehensive metrics", exc_info=True)
            raise MetricCollectionError("Failed to collect metrics") from e

    @handle_errors(default='insufficient_data')
    def calculate_trend(self, metric_type: str) -> str:
        """
        Calculate trend for a specific metric based on recent history.
        
        Args:
            metric_type: Type of metric to calculate trend for (e.g., 'cpu', 'memory')
            
        Returns:
            str: Trend direction ('increasing', 'decreasing', 'stable', or 'insufficient_data')
        """
        try:
            history = self.metrics_history.get(metric_type, [])
            if len(history) < 10:
                logger.debug(f"Insufficient data points for {metric_type} trend analysis")
                return 'insufficient_data'

            # Get recent values (last 10 data points)
            recent_values = list(history)[-10:]
            
            # Simple linear regression to determine trend
            x = np.arange(len(recent_values))
            y = np.array([v.get('value', 0) for v in recent_values if v])
            
            if len(y) < 2:
                return 'insufficient_data'
                
            # Calculate slope
            z = np.polyfit(x[-len(y):], y, 1)
            slope = z[0]
            
            # Determine trend based on slope
            if abs(slope) < 0.1:  # Threshold for considering a trend significant
                return 'stable'
            elif slope > 0:
                return 'increasing'
            else:
                return 'decreasing'
                
        except Exception as e:
            logger.error(f"Error calculating {metric_type} trend: {e}", exc_info=True)
            return 'error'

    @handle_errors()
    def update_metrics_history(self, metrics: Dict[str, Any]) -> None:
        """
        Update metrics history with new data.
        
        Args:
            metrics: Dictionary containing system metrics
        """
        try:
            timestamp = metrics.get('timestamp')
            if not timestamp:
                logger.warning("No timestamp in metrics, using current time")
                timestamp = datetime.utcnow().isoformat()
            
            # Update history for each metric type
            for metric_type, history in self.metrics_history.items():
                if metric_type in metrics:
                    metric_data = metrics[metric_type]
                    if isinstance(metric_data, dict):
                        # For complex metrics, store a summary
                        history.append({
                            'timestamp': timestamp,
                            'value': self._extract_metric_value(metric_type, metric_data),
                            'raw': metric_data
                        })
            
            logger.debug(f"Updated metrics history with new data at {timestamp}")
            
        except Exception as e:
            logger.error(f"Error updating metrics history: {e}", exc_info=True)
            raise
    
    def _extract_metric_value(self, metric_type: str, metric_data: Dict[str, Any]) -> float:
        """Extract a representative value from a metric for trend analysis."""
        try:
            if metric_type == 'cpu':
                return metric_data.get('usage_percent', 0)
            elif metric_type == 'memory':
                return metric_data.get('virtual', {}).get('percent', 0)
            elif metric_type == 'disk':
                # Return average disk usage across all partitions
                usages = [
                    part.get('usage', {}).get('percent', 0) 
                    for part in metric_data.values() 
                    if isinstance(part, dict)
                ]
                return sum(usages) / len(usages) if usages else 0
            elif metric_type == 'network':
                # Return total bytes sent + received
                io = metric_data.get('io', {})
                return (io.get('bytes_sent', 0) + io.get('bytes_recv', 0)) / (1024 * 1024)  # MB
            return 0
        except Exception as e:
            logger.warning(f"Error extracting {metric_type} value: {e}")
            return 0

    @handle_errors()
    def store_metrics_db(self, metrics: Dict[str, Any]) -> None:
        """
        Store metrics in the database with error handling and batch processing.
        
        Args:
            metrics: Dictionary containing system metrics
        """
        if not metrics:
            logger.warning("No metrics provided for storage")
            return
            
        timestamp = metrics.get('timestamp', datetime.utcnow().isoformat())
        
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare batch insert for metrics
                metrics_batch = []
                
                # Flatten metrics for storage
                for metric_type, value in metrics.items():
                    if metric_type == 'timestamp':
                        continue
                        
                    if isinstance(value, dict):
                        # For complex metrics, store as JSON
                        metrics_batch.append((timestamp, metric_type, 0, json.dumps(value)))
                    elif isinstance(value, (int, float)):
                        # For simple metrics, store as numeric value
                        metrics_batch.append((timestamp, metric_type, float(value), None))
                
                # Batch insert
                if metrics_batch:
                    cursor.executemany("""
                        INSERT INTO metrics (timestamp, metric_type, value, metadata)
                        VALUES (?, ?, ?, ?)
                    """, metrics_batch)
                    
                    conn.commit()
                    logger.debug(f"Stored {len(metrics_batch)} metrics in database")
                    
        except Exception as e:
            logger.error(f"Error storing metrics in database: {e}", exc_info=True)
            raise DatabaseError("Failed to store metrics") from e

    @handle_errors()
    def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in the collected metrics.
        
        Args:
            metrics: Dictionary containing system metrics
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        timestamp = metrics.get('timestamp', datetime.utcnow().isoformat())
        
        try:
            # CPU anomaly detection
            cpu_usage = metrics.get('cpu', {}).get('usage_percent', 0)
            if cpu_usage > self.anomaly_thresholds['cpu_usage']:
                anomalies.append({
                    'timestamp': timestamp,
                    'anomaly_type': 'high_cpu_usage',
                    'severity': 'warning' if cpu_usage < 90 else 'critical',
                    'details': f"CPU usage is {cpu_usage:.1f}% (threshold: {self.anomaly_thresholds['cpu_usage']}%)"
                })
            
            # Memory anomaly detection
            mem_usage = metrics.get('memory', {}).get('virtual', {}).get('percent', 0)
            if mem_usage > self.anomaly_thresholds['memory_usage']:
                anomalies.append({
                    'timestamp': timestamp,
                    'anomaly_type': 'high_memory_usage',
                    'severity': 'warning' if mem_usage < 95 else 'critical',
                    'details': f"Memory usage is {mem_usage:.1f}% (threshold: {self.anomaly_thresholds['memory_usage']}%)"
                })
            
            # Disk anomaly detection
            for device, disk_data in metrics.get('disk', {}).items():
                if not isinstance(disk_data, dict):
                    continue
                    
                usage = disk_data.get('usage', {})
                disk_usage = usage.get('percent', 0)
                
                if disk_usage > self.anomaly_thresholds['disk_usage']:
                    mountpoint = disk_data.get('mountpoint', 'unknown')
                    anomalies.append({
                        'timestamp': timestamp,
                        'anomaly_type': 'high_disk_usage',
                        'severity': 'warning' if disk_usage < 95 else 'critical',
                        'details': (
                            f"Disk usage on {device} ({mountpoint}) is {disk_usage:.1f}% "
                            f"(threshold: {self.anomaly_thresholds['disk_usage']}%)"
                        )
                    })
            
            # Store anomalies in database
            if anomalies:
                with self._get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.executemany("""
                        INSERT INTO anomalies (timestamp, anomaly_type, severity, details)
                        VALUES (?, ?, ?, ?)
                    """, [
                        (
                            anom['timestamp'],
                            anom['anomaly_type'],
                            anom['severity'],
                            anom['details']
                        )
                        for anom in anomalies
                    ])
                    conn.commit()
                
                logger.warning(f"Detected {len(anomalies)} anomalies")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}", exc_info=True)
            raise
    
    def cleanup(self) -> None:
        """Clean up resources and ensure proper shutdown."""
        try:
            # Clear any cached data
            self._get_cpu_metrics.cache_clear()
            self._get_memory_metrics.cache_clear()
            
            # Close database connection if it exists
            if hasattr(self, '_db_conn') and self._db_conn:
                try:
                    self._db_conn.close()
                except Exception as e:
                    logger.error(f"Error closing database connection: {e}")
            
            logger.info("System monitor shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
        finally:
            # Ensure all handlers are flushed
            for handler in logger.handlers:
                handler.flush()
    
    def __del__(self):
        """Ensure resources are cleaned up when the object is destroyed."""
        self.cleanup()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current system state.
        
        Returns:
            Dictionary with system metrics summary
        """
        metrics = self.collect_comprehensive_metrics()
        
        return {
            'timestamp': metrics.get('timestamp'),
            'cpu': {
                'usage_percent': metrics.get('cpu', {}).get('usage_percent'),
                'load_avg': metrics.get('cpu', {}).get('load_avg')
            },
            'memory': {
                'percent': metrics.get('memory', {}).get('virtual', {}).get('percent'),
                'available_gb': round(metrics.get('memory', {}).get('virtual', {}).get('available', 0) / (1024**3), 2)
            },
            'disk': {
                'total_devices': len(metrics.get('disk', {})),
                'devices': [
                    {
                        'device': dev,
                        'mountpoint': data.get('mountpoint'),
                        'usage_percent': data.get('usage', {}).get('percent')
                    }
                    for dev, data in metrics.get('disk', {}).items()
                ]
            },
            'processes': {
                'total': metrics.get('processes', {}).get('total', 0),
                'top_cpu': [
                    {'pid': p.get('pid'), 'name': p.get('name'), 'cpu_percent': p.get('cpu_percent')}
                    for p in metrics.get('processes', {}).get('top_cpu', [])[:3]
                ]
            }
        }
