# Performance Optimization Guide

This guide provides recommendations and best practices for optimizing the performance of the OPRYXX_LOGS application.

## Table of Contents
- [Performance Monitoring](#performance-monitoring)
- [Database Optimization](#database-optimization)
- [Caching Strategy](#caching-strategy)
- [Resource Management](#resource-management)
- [Performance Testing](#performance-testing)
- [Troubleshooting](#troubleshooting)

## Performance Monitoring

The application includes a built-in performance monitoring system that tracks:

- Function execution times
- Database query performance
- System resource usage (CPU, memory, disk I/O, network)

### Enabling Performance Monitoring

1. **Basic Monitoring**:
   ```python
   from core.performance import PerformanceMonitor
   
   # Get the global monitor instance
   monitor = PerformanceMonitor()
   
   # Monitor a function
   @monitor.monitor("my_function")
   def my_function():
       # Your code here
       pass
   ```

2. **Resource Monitoring**:
   ```python
   from core.monitoring import start_monitoring, stop_monitoring
   
   # Start monitoring system resources
   start_monitoring()
   
   # Your application code
   
   # Stop monitoring when done
   stop_monitoring()
   ```

## Database Optimization

### Indexing

- Create indexes on frequently queried columns:
  ```python
  from sqlalchemy import Index
  
  # Create an index on the 'name' column
  idx_name = Index('idx_test_name', TestModel.name)
  ```

### Query Optimization

1. **Use EXPLAIN ANALYZE**:
   ```python
   from core.db_utils import DatabaseManager
   
   db_manager = DatabaseManager(engine)
   plan = db_manager.get_query_plan("SELECT * FROM test_table WHERE value > 100")
   print(plan)
   ```

2. **Optimization Tips**:
   - Use `select_related()` and `joinedload()` to reduce the number of queries
   - Avoid `SELECT *` - only fetch the columns you need
   - Use `yield_per()` for large result sets
   - Consider using read replicas for read-heavy workloads

### Connection Pooling

The application uses SQLAlchemy's connection pooling by default. Configure pool settings in your database URL:

```python
# Example with connection pooling
DATABASE_URL = "postgresql+psycopg2://user:pass@localhost/dbname?pool_size=10&max_overflow=20"
```

## Caching Strategy

The application includes a flexible caching system with support for multiple backends.

### Basic Usage

```python
from core.caching import CacheManager

# Get cache instance
cache = CacheManager()

# Set a value with TTL (in seconds)
cache.set("user:123", user_data, ttl=300)

# Get a value
user = cache.get("user:123")


# Delete a value
cache.delete("user:123")
```

### Cache Invalidation

1. **Time-based Invalidation**:
   - Set appropriate TTL values based on data freshness requirements
   - Use shorter TTLs for rapidly changing data

2. **Event-based Invalidation**:
   ```python
   def update_user(user_id, data):
       # Update user in database
       db.update_user(user_id, data)
       
       # Invalidate cache
       cache.delete(f"user:{user_id}")
   ```

### Multi-level Caching

For high-traffic applications, consider implementing a multi-level cache:

1. L1: In-memory cache (fastest, per-process)
2. L2: Distributed cache (e.g., Redis)
3. L3: Database (source of truth)

## Resource Management

### Monitoring System Resources

The resource monitor tracks:

- CPU usage
- Memory usage
- Disk I/O
- Network I/O

```python
from core.monitoring import get_resource_monitor

monitor = get_resource_monitor()

# Get current resource usage
usage = monitor.get_usage_summary()
print(f"CPU: {usage['cpu_percent']}%")
print(f"Memory: {usage['memory_percent']}%")
```

### Identifying Bottlenecks

1. **Check for resource limits**:
   ```python
   issues = monitor.check_resource_limits()
   if issues:
       for resource, message in issues.items():
           print(f"{resource}: {message}")
   ```

2. **Analyze slow queries**:
   ```python
   from core.db_utils import get_db
   
   db = get_db()
   slow_queries = db.profiler.slow_queries
   for query in slow_queries:
       print(f"Slow query ({query['duration']:.3f}s): {query['statement']}")
   ```

## Performance Testing

### Running Benchmarks

1. **Run all benchmarks**:
   ```bash
   python -m benchmarks.performance_benchmark
   ```

2. **Run specific benchmark tests**:
   ```bash
   pytest tests/test_benchmarks.py -v
   ```

### Interpreting Results

- Look for operations with high average execution times
- Identify operations with high standard deviations (inconsistent performance)
- Compare results across different environments

## Troubleshooting

### Common Issues

1. **High CPU Usage**:
   - Check for tight loops or CPU-intensive operations
   - Profile the application to identify hot spots
   - Consider using async I/O for I/O-bound operations

2. **Memory Leaks**:
   - Monitor memory usage over time
   - Use tools like `tracemalloc` to track memory allocations
   - Look for circular references or large object caches

3. **Slow Database Queries**:
   - Use `EXPLAIN ANALYZE` to analyze query plans
   - Add appropriate indexes
   - Consider denormalizing data for read-heavy operations

### Performance Metrics

Monitor these key metrics:

- **Application Level**:
  - Request/response times
  - Error rates
  - Throughput (requests/second)

- **System Level**:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network I/O

## Best Practices

1. **Regular Monitoring**:
   - Set up alerts for abnormal behavior
   - Monitor both application and system metrics
   - Keep historical data for trend analysis

2. **Continuous Optimization**:
   - Regularly profile your application
   - Update dependencies
   - Test with production-like data

3. **Capacity Planning**:
   - Monitor growth trends
   - Plan for scaling before it's needed
   - Consider both vertical and horizontal scaling options
