"""Performance tracking and historical data management"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import psutil
import platform
import json

class PerformanceTracker:
    """Tracks and manages historical performance metrics"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the performance tracker"""
        self.db_path = db_path or str(Path.home() / ".opryxx" / "performance.db")
        self._init_db()
        self._stop_event = threading.Event()
        self._collector_thread = None
    
    def _init_db(self) -> None:
        """Initialize the database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics (timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_type 
                ON metrics (metric_type)
            """)
            
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def start_collector(self, interval: int = 60) -> None:
        """Start the background metrics collector"""
        if self._collector_thread and self._collector_thread.is_alive():
            return
            
        self._stop_event.clear()
        self._collector_thread = threading.Thread(
            target=self._collect_metrics_loop,
            args=(interval,),
            daemon=True
        )
        self._collector_thread.start()
    
    def stop_collector(self) -> None:
        """Stop the background metrics collector"""
        self._stop_event.set()
        if self._collector_thread and self._collector_thread.is_alive():
            self._collector_thread.join(timeout=5)
    
    def _collect_metrics_loop(self, interval: int) -> None:
        """Background loop to collect metrics at regular intervals"""
        while not self._stop_event.is_set():
            try:
                self.collect_system_metrics()
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            # Wait for the interval, but check for stop event more frequently
            for _ in range(interval * 10):
                if self._stop_event.wait(0.1):
                    return
    
    def collect_system_metrics(self) -> None:
        """Collect system metrics and store them in the database"""
        timestamp = datetime.utcnow()
        metrics = []
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append((timestamp, 'cpu.usage', cpu_percent, {}))
        
        # Memory metrics
        mem = psutil.virtual_memory()
        metrics.extend([
            (timestamp, 'memory.percent', mem.percent, {}),
            (timestamp, 'memory.used', mem.used, {}),
            (timestamp, 'memory.available', mem.available, {})
        ])
        
        # Disk metrics
        try:
            disk = psutil.disk_usage('/')
            metrics.extend([
                (timestamp, 'disk.usage', disk.percent, {}),
                (timestamp, 'disk.used', disk.used, {}),
                (timestamp, 'disk.free', disk.free, {})
            ])
        except Exception as e:
            print(f"Error collecting disk metrics: {e}")
        
        # Network metrics
        try:
            net_io = psutil.net_io_counters()
            metrics.extend([
                (timestamp, 'network.bytes_sent', net_io.bytes_sent, {}),
                (timestamp, 'network.bytes_recv', net_io.bytes_recv, {})
            ])
        except Exception as e:
            print(f"Error collecting network metrics: {e}")
        
        # System load (if available)
        try:
            load_avg = psutil.getloadavg()
            for i, load in enumerate(load_avg, 1):
                metrics.append((timestamp, f'system.load_avg_{i}m', load, {}))
        except (AttributeError, OSError):
            pass  # getloadavg not available on Windows
        
        # Store all metrics
        self.add_metrics(metrics)
    
    def add_metrics(self, metrics: List[Tuple[datetime, str, float, Dict]]) -> None:
        """Add multiple metrics to the database"""
        with self._get_connection() as conn:
            conn.executemany(
                """
                INSERT INTO metrics (timestamp, metric_type, value, metadata)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (ts.isoformat(), metric_type, value, json.dumps(metadata))
                    for ts, metric_type, value, metadata in metrics
                ]
            )
            conn.commit()
    
    def get_metrics(
        self,
        metric_type: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Retrieve metrics of a specific type within a time range"""
        query = "SELECT * FROM metrics WHERE metric_type = ?"
        params = [metric_type]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        if limit > 0:
            query += " LIMIT ?"
            params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_metric_summary(
        self,
        metric_type: str,
        period: str = '24h',
        aggregation: str = 'avg'
    ) -> Dict[str, Any]:
        """Get aggregated metric data for a time period"""
        end_time = datetime.utcnow()
        
        if period == '1h':
            start_time = end_time - timedelta(hours=1)
            interval = '5 minutes'
        elif period == '24h':
            start_time = end_time - timedelta(days=1)
            interval = '1 hour'
        elif period == '7d':
            start_time = end_time - timedelta(days=7)
            interval = '6 hours'
        elif period == '30d':
            start_time = end_time - timedelta(days=30)
            interval = '1 day'
        else:
            raise ValueError(f"Unsupported period: {period}")
        
        # SQLite doesn't have built-in time bucketing, so we'll use strftime
        # This is a simplified approach - in production, you might want to use a more robust solution
        time_format = {
            '5 minutes': '%Y-%m-%d %H:%M:00',
            '1 hour': '%Y-%m-%d %H:00:00',
            '6 hours': '%Y-%m-%d %H:00:00',  # Simplified
            '1 day': '%Y-%m-%d 00:00:00'
        }[interval]
        
        query = f"""
        SELECT 
            strftime(?, timestamp) as bucket,
            {aggregation}(value) as value_agg,
            COUNT(*) as sample_count
        FROM metrics
        WHERE metric_type = ? 
          AND timestamp BETWEEN ? AND ?
        GROUP BY bucket
        ORDER BY bucket
        """
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                query,
                (
                    time_format,
                    metric_type,
                    start_time.isoformat(),
                    end_time.isoformat()
                )
            )
            
            results = [dict(row) for row in cursor.fetchall()]
            
            # Convert string timestamps back to datetime objects
            for row in results:
                row['timestamp'] = datetime.fromisoformat(row['bucket'])
                del row['bucket']
            
            return {
                'metric_type': metric_type,
                'start_time': start_time,
                'end_time': end_time,
                'interval': interval,
                'data': results
            }
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> int:
        """Remove metrics older than the specified number of days"""
        cutoff = (datetime.utcnow() - timedelta(days=days_to_keep)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM metrics WHERE timestamp < ?",
                (cutoff,)
            )
            deleted_rows = cursor.rowcount
            conn.commit()
            
            # Vacuum to reclaim disk space
            if deleted_rows > 0:
                conn.execute("VACUUM")
            
            return deleted_rows
    
    def __del__(self):
        """Ensure background thread is stopped when the object is destroyed"""
        self.stop_collector()

# Singleton instance for easy access
tracker = PerformanceTracker()
