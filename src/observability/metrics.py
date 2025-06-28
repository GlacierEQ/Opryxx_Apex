from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import functools
import logging

logger = logging.getLogger(__name__)

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

MODEL_INFERENCE_DURATION = Histogram(
    'model_inference_duration_seconds',
    'Model inference duration',
    ['model_name']
)

ERROR_COUNT = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()

    def track_request(self, method: str, endpoint: str, status: int):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()

    def track_request_duration(self, method: str, endpoint: str, duration: float):
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def track_model_inference(self, model_name: str, duration: float):
        MODEL_INFERENCE_DURATION.labels(model_name=model_name).observe(duration)

    def track_error(self, error_type: str, endpoint: str):
        ERROR_COUNT.labels(error_type=error_type, endpoint=endpoint).inc()

    def increment_active_connections(self):
        ACTIVE_CONNECTIONS.inc()

    def decrement_active_connections(self):
        ACTIVE_CONNECTIONS.dec()

# Global metrics instance
metrics = MetricsCollector()

def track_performance(func):
    """Decorator to track function performance"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            metrics.track_model_inference(func
