""
System resource monitoring and performance tracking.
"""
    """System resource metrics."""
    """Monitors system resources and application performance metrics."""
        """Initialize the resource monitor."""
        """Initialize Prometheus metrics."""
        """Update system metrics."""
        """Update Prometheus metrics."""
        """Main monitoring loop."""
        """Start the monitoring thread."""
        """Stop the monitoring thread."""
        """
        """
            raise ValueError(f"Unknown metric: {metric}")
            
        with self._lock:
            history = list(self._metrics_history[metric])
        
        if time_window is not None:
            cutoff = time.time() - time_window
            history = [point for point in history if point[0] >= cutoff]
            
        return history
    
    def get_current_metrics(self) -> SystemMetrics:
        """Get the current system metrics."""
        """Get a summary of current resource usage."""
        """Check if any resource limits are being approached."""
            issues['cpu'] = f"High CPU usage: {metrics.cpu_percent:.1f}%"
            
        if metrics.memory_percent > performance_config.MAX_MEMORY_USAGE_PERCENT:
            issues['memory'] = f"High memory usage: {metrics.memory_percent:.1f}%"
        
        # Check disk space
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:  # 90% disk usage threshold
                    issues[f'disk_{partition.mountpoint}'] = (
                        f"High disk usage on {partition.mountpoint}: {usage.percent:.1f}%"
                    )
            except Exception:
                continue
                
        return issues


def start_prometheus_server(port: int = 8000) -> None:
    """Start a Prometheus metrics server."""
        print(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        print(f"Failed to start Prometheus metrics server: {e}")


# Global instance
resource_monitor: Optional[ResourceMonitor] = None

def get_resource_monitor() -> ResourceMonitor:
    """Get or create the global resource monitor instance."""
    """Start system resource monitoring."""
    """Stop system resource monitoring."""